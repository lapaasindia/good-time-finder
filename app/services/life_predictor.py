"""
Life Predictor Service — unified orchestrator.

Combines:
- Rule-based muhurtha engine
- Dasha engine
- Yoga engine
- Shadbala strength
- Gochara transit scoring
- Ashtakavarga bonus
- Per-category ranking weights
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.astrology.ashtakavarga import ashtakavarga_bonus, transit_strength as avk_transit_strength
from app.astrology.calculations import (
    build_context,
    natal_lagna,
    natal_moon_sign,
    planet_houses,
    planet_signs,
)
from app.astrology.gochara import category_gochara_score, GOOD_HOUSES_FROM_NATAL_MOON, _house_from_sign
from app.astrology.shadbala import benefic_strength_score, lagna_lord_strength, shadbala_summary
from app.astrology.dasha import CATEGORY_PLANETS
from app.astrology.sade_sati import compute_sade_sati
from app.astrology.special_conditions import compute_special_conditions, apply_combustion_to_shadbala, get_raw_longitudes, get_speeds
from app.astrology.divisional_charts import navamsa_score_for_category, dasamsa_score_for_category, hora_score_for_category, saptamsa_score_for_category, vimsopaka_for_category
from app.astrology.panchang import build_panchang
from app.astrology.tara_bala import compute_tara, chandra_bala
from app.astrology.avasthas import avastha_score_for_planets, pushkara_bonus, transit_speed_weight
from app.astrology.jaimini import compute_chara_karakas, compute_arudha_lagna, jaimini_karaka_score, arudha_lagna_score
from app.astrology.gulika_mandi import estimate_gulika_sign, gulika_penalty, badhaka_penalty
from app.astrology.sudarshana import sudarshana_aggregate
from app.config import load_event_catalog
from app.core.dasha_engine import DashaEngine
from app.core.engine import GoodTimeEngine, evaluate_event_at_context
from app.core.enums import EventTag, ZODIAC_SIGNS as _ZODIAC_SIGNS
from app.core.models import EventDefinition, GeoLocation, Person, TimeRange, TimeWindow
from app.core.ranking import compute_composite_score, get_weights, rank_window
from app.core.windows import merge_slices_to_windows
from app.core.yoga_engine import YogaEngine
from app.rules.registry import build_default_registry


@dataclass
class PredictionWindow:
    start: datetime
    end: datetime
    nature: str
    composite_score: float
    rank: float
    duration_minutes: float
    active_events: list[str] = field(default_factory=list)
    dasha_active: list[str] = field(default_factory=list)
    yogas_active: list[str] = field(default_factory=list)
    gochara_score: float = 0.0
    shadbala_score: float = 0.0
    dasha_bonus: float = 0.0
    yoga_score: float = 0.0
    ashtakavarga_bonus: float = 0.0
    rule_score: float = 0.0


@dataclass
class LifePrediction:
    category: str
    person_name: str
    time_range_start: datetime
    time_range_end: datetime
    natal_lagna: str
    natal_moon_sign: str
    active_dashas: list[dict]
    yogas: list[dict]
    shadbala: dict[str, float]
    gochara_score: float
    sade_sati: dict
    special_conditions: dict
    panchang_score: float
    windows: list[PredictionWindow]
    top_windows: list[PredictionWindow]
    overall_period_score: float
    narrative: str


# ── Yoga-Dasha Activation ──
# Maps yoga names to the planets that form them. When the current dasha lord
# matches a yoga's forming planets, the yoga is "activated" and contributes more.
YOGA_FORMING_PLANETS: dict[str, set[str]] = {
    "RajaYoga":              {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"},
    "DhanaYoga":             {"Jupiter", "Venus", "Mercury", "Moon"},
    "GajakesariYoga":        {"Jupiter", "Moon"},
    "BudhaAdityaYoga":       {"Sun", "Mercury"},
    "ChandraMangalYoga":     {"Moon", "Mars"},
    "SanyasaYoga":           {"Saturn", "Ketu", "Jupiter"},
    "YogakarakaYoga":        {"Saturn", "Venus", "Mars"},
    "RuchakaYoga":           {"Mars"},
    "BhadraYoga":            {"Mercury"},
    "HamsaYoga":             {"Jupiter"},
    "MalavyaYoga":           {"Venus"},
    "ShashaYoga":            {"Saturn"},
    "NeechaBhangarajaYoga":  {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"},
    "ViparitagajaYoga":      {"Mars", "Saturn", "Jupiter"},
    "SaraswatiYoga":         {"Mercury", "Venus", "Jupiter"},
    "LakshmiYoga":           {"Venus", "Jupiter"},
    "ChandraAdhiYoga":       {"Mercury", "Venus", "Jupiter"},
    "VesiYoga":              {"Mercury", "Venus", "Mars", "Jupiter", "Saturn"},
    "VasiYoga":              {"Mercury", "Venus", "Mars", "Jupiter", "Saturn"},
    "UbhayachariYoga":       {"Mercury", "Venus", "Mars", "Jupiter", "Saturn"},
    "SunaphaYoga":           {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"},
    "AnaphaYoga":            {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"},
    "DurudharaYoga":         {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"},
    "KemdrumYoga":           {"Moon"},
    "KemdrumBhanga":         {"Venus", "Jupiter", "Mercury"},
    "AmalaYoga":             {"Mercury", "Venus", "Jupiter"},
    "ShakataYoga":           {"Moon", "Jupiter"},
    "GuruMangalYoga":        {"Jupiter", "Mars"},
    "ParivartanaYoga":       {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"},
}


def _yoga_dasha_activation(
    active_yogas: list[dict],
    maha_planet: str | None,
    antar_planet: str | None,
) -> float:
    """Return a multiplier (0.9 to 1.2) based on how many active yogas
    are 'activated' by the current dasha lords.

    Conservative range to avoid over-optimization per user feedback."""
    if not active_yogas or not maha_planet:
        return 1.0

    dasha_lords = {maha_planet}
    if antar_planet:
        dasha_lords.add(antar_planet)

    total_yogas = len(active_yogas)
    activated = 0
    for y in active_yogas:
        name = y["name"] if isinstance(y, dict) else y.name
        forming = YOGA_FORMING_PLANETS.get(name, set())
        if forming & dasha_lords:
            activated += 1

    ratio = activated / total_yogas if total_yogas else 0.0
    # Conservative range: 0% activated → 0.9×, 100% activated → 1.2×
    return 0.9 + ratio * 0.3


class LifePredictorService:
    def __init__(self) -> None:
        self._registry = build_default_registry()
        self._catalog = load_event_catalog()
        self._engine = GoodTimeEngine(registry=self._registry)

    def predict(
        self,
        person: Person,
        location: GeoLocation,
        time_range: TimeRange,
        category: str,
    ) -> LifePrediction:
        tag = EventTag(category)
        selected_events = [e for e in self._catalog if tag in e.tags]

        n_moon = natal_moon_sign(person)
        n_lagna = natal_lagna(person)
        natal_p_signs = planet_signs(person.birth_datetime, person.birth_location)
        natal_p_houses = planet_houses(person.birth_datetime, person.birth_location)

        raw_shadbala = shadbala_summary(natal_p_signs, natal_p_houses)
        relevant_planets = CATEGORY_PLANETS.get(category, set())

        special = compute_special_conditions(
            person.birth_datetime, natal_p_houses, natal_p_signs, n_lagna
        )
        shadbala = apply_combustion_to_shadbala(
            raw_shadbala, special.combustion, special.retrograde
        )

        # Natal longitudes for divisional charts (D9 Navamsa, D10 Dasamsa, D2, D3, D7)
        natal_longitudes = get_raw_longitudes(person.birth_datetime)
        d9_score = navamsa_score_for_category(
            natal_longitudes, natal_p_signs, category, relevant_planets
        )
        d10_score = dasamsa_score_for_category(
            natal_longitudes, natal_p_signs, category, relevant_planets
        )
        d2_score = hora_score_for_category(
            natal_longitudes, category, relevant_planets
        )
        d7_score = saptamsa_score_for_category(
            natal_longitudes, natal_p_signs, category, relevant_planets
        )
        vimsopaka_score = vimsopaka_for_category(
            natal_longitudes, natal_p_signs, relevant_planets
        )
        # Combined divisional chart bonus (natal, computed once)
        divisional_bonus = (d9_score * 0.3 + d10_score * 0.3 +
                          d2_score * 0.15 + d7_score * 0.1 +
                          vimsopaka_score * 0.15)

        # Jaimini Chara Karakas and Arudha Lagna
        chara_karakas = compute_chara_karakas(natal_longitudes)
        arudha_lagna = compute_arudha_lagna(n_lagna, natal_p_signs)
        jaimini_score = jaimini_karaka_score(
            chara_karakas, natal_p_signs, natal_p_houses, n_lagna, category
        )
        arudha_score = arudha_lagna_score(arudha_lagna, n_lagna, category)

        # Gulika/Mandi and Badhaka
        weekday = person.birth_datetime.strftime("%A")
        birth_hour = person.birth_datetime.hour + person.birth_datetime.minute / 60.0
        gulika_sign = estimate_gulika_sign(weekday, birth_hour, n_lagna)
        gulika_pen = gulika_penalty(gulika_sign, natal_p_houses, n_lagna)
        badhaka_pen = badhaka_penalty(n_lagna, natal_p_houses, category)

        # Natal Sun sign for Chandra Bala and Sudarshana
        natal_sun_sign = natal_p_signs.get("Sun", "")

        sade_sati = compute_sade_sati(n_moon, time_range.start)
        sade_sati_penalty = sade_sati.penalty
        sade_sati_dict = {
            "active": sade_sati.currently_active,
            "phase": sade_sati.current_phase.phase if sade_sati.current_phase else None,
            "dhaiya": sade_sati.dhaiya_active,
            "summary": sade_sati.summary(),
            "penalty": sade_sati_penalty,
        }

        dasha_engine = DashaEngine(person, lagna=n_lagna, planet_strengths=shadbala, natal_houses=natal_p_houses)
        yoga_engine = YogaEngine(person)
        raw_yoga_score = yoga_engine.score_for_category(category)
        yoga_score = max(-2.0, min(2.0, raw_yoga_score * 0.4))
        active_yogas = [
            {"name": y.name, "strength": y.strength, "description": y.description}
            for y in yoga_engine.active_yogas
        ]

        active_dasha_info: list[dict] = []
        maha, antar, prat = dasha_engine.active_full_at(time_range.start)

        # Yoga-Dasha Activation: modulate yoga score based on dasha lord match
        yoga_activation = _yoga_dasha_activation(
            active_yogas,
            maha.planet if maha else None,
            antar.planet if antar else None,
        )
        yoga_score = round(yoga_score * yoga_activation, 3)
        if maha:
            active_dasha_info.append({
                "level": "mahadasha",
                "planet": maha.planet,
                "start": maha.start.isoformat(),
                "end": maha.end.isoformat(),
            })
        if antar:
            active_dasha_info.append({
                "level": "antardasha",
                "planet": antar.planet,
                "start": antar.start.isoformat(),
                "end": antar.end.isoformat(),
            })
        if prat:
            active_dasha_info.append({
                "level": "pratyantardasha",
                "planet": prat.planet,
                "start": prat.start.isoformat(),
                "end": prat.end.isoformat(),
            })

        from app.core.engine import generate_slices
        time_points = generate_slices(time_range)

        sha_bonus = benefic_strength_score(shadbala, relevant_planets)
        sha_centered = sha_bonus - 1.0

        lagna_lord_bonus = lagna_lord_strength(n_lagna, shadbala, natal_p_houses)

        @dataclass
        class _SlotScore:
            dt: datetime
            rule_score: float
            gochara: float
            dasha_b: float
            avarga: float
            panchang_s: float
            tara_score: float
            chandra_bala_score: float
            avastha_score: float
            pushkara_bonus_score: float
            sudarshana_score: float
            sandhi_penalty: float
            active_events: list[str]
            nature: str

        slot_scores: list[_SlotScore] = []

        for dt in time_points:
            ctx = build_context(dt, location, person)
            current_p_signs = ctx.planet_signs

            # Retrograde detection for transit planets
            transit_speeds = get_speeds(dt)
            retro_planets = {p for p, spd in transit_speeds.items() if spd < 0}

            # ── Tara Bala (Nakshatra transit strength) ──
            from app.astrology.calculations import moon_constellation
            transit_nakshatra = moon_constellation(dt, location)
            natal_nakshatra = moon_constellation(person.birth_datetime, person.birth_location)
            _, tara_score = compute_tara(natal_nakshatra, transit_nakshatra)

            # Chandra Bala — Moon's transit strength
            transit_moon_house = _house_from_sign(current_p_signs.get("Moon", ""), n_moon)
            chandra_bala_score = chandra_bala(transit_moon_house)

            # ── Planetary Avasthas (age states) ──
            transit_longitudes = get_raw_longitudes(dt)
            avastha_score = avastha_score_for_planets(transit_longitudes, relevant_planets)

            # ── Pushkara Navamsa bonus ──
            transit_moon_lon = transit_longitudes.get("Moon", 0)
            transit_lagna_lon = transit_longitudes.get("Lagna", 0) if "Lagna" in transit_longitudes else 0
            pushkara_bonus_score = pushkara_bonus(transit_moon_lon, transit_lagna_lon)

            # ── Sudarshana Chakra (triple-perspective transit) ──
            transit_sun_sign = current_p_signs.get("Sun", "")
            sudarshana_score = sudarshana_aggregate(
                current_p_signs, n_lagna, n_moon, natal_sun_sign
            )

            # ── Dasha Sandhi (junction penalty) ──
            sandhi_penalty = dasha_engine.dasha_sandhi_penalty(dt)

            gochara = category_gochara_score(current_p_signs, n_moon, CATEGORY_PLANETS.get(category, set()), natal_lagna=n_lagna, natal_planet_signs=natal_p_signs, retrograde_planets=retro_planets)
            avarga = ashtakavarga_bonus(current_p_signs, natal_p_signs, n_lagna)
            # Transit-dasha correlation: only include planets in STRONG transit
            # (i.e., in good houses from natal Moon) as meaningful triggers
            strong_transiting = set()
            for _tp, _ts in current_p_signs.items():
                if _ts in _ZODIAC_SIGNS:
                    _h = _house_from_sign(_ts, n_moon)
                    if _h in GOOD_HOUSES_FROM_NATAL_MOON.get(_tp, set()):
                        strong_transiting.add(_tp)
            dasha_b = dasha_engine.dasha_bonus(dt, category, transiting_planets=strong_transiting)
            
            # Ashtakavarga strength of dasha lord in its transit sign
            # High bindus = planet delivers results, low bindus = blocked
            _maha, _antar, _ = dasha_engine.active_full_at(dt)
            _avk_planets = {"Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"}
            if _maha:
                maha_transit_sign = current_p_signs.get(_maha.planet, "")
                if maha_transit_sign and _maha.planet in _avk_planets:
                    maha_bindus = avk_transit_strength(_maha.planet, maha_transit_sign, natal_p_signs, n_lagna)
                    dasha_b += (maha_bindus - 4.0) * 0.2
            if _antar:
                antar_transit_sign = current_p_signs.get(_antar.planet, "")
                if antar_transit_sign and _antar.planet in _avk_planets:
                    antar_bindus = avk_transit_strength(_antar.planet, antar_transit_sign, natal_p_signs, n_lagna)
                    dasha_b += (antar_bindus - 4.0) * 0.1

            pang = build_panchang(dt, ctx.moon_constellation, ctx.lunar_day, ctx.weekday)
            pang_score = pang.yoga_score + pang.karana_score

            slot_rule_total = 0.0
            slot_events: list[str] = []
            for event_def in selected_events:
                hit = evaluate_event_at_context(event_def, ctx, person, self._registry)
                if hit:
                    slot_rule_total += hit.score
                    slot_events.append(event_def.name)

            slot_scores.append(_SlotScore(
                dt=dt,
                rule_score=slot_rule_total,
                gochara=gochara,
                dasha_b=dasha_b,
                avarga=avarga,
                panchang_s=pang_score,
                tara_score=tara_score,
                chandra_bala_score=chandra_bala_score,
                avastha_score=avastha_score,
                pushkara_bonus_score=pushkara_bonus_score,
                sudarshana_score=sudarshana_score,
                sandhi_penalty=sandhi_penalty,
                active_events=slot_events,
                nature="",
            ))

        if not slot_scores:
            mid_dt = time_range.start
            mid_ctx = build_context(mid_dt, location, person)
            mid_gochara = 0.0
            panchang = build_panchang(mid_dt, mid_ctx.moon_constellation, mid_ctx.lunar_day, mid_ctx.weekday)
            panchang_score = panchang.yoga_score + panchang.karana_score
        else:
            mid_idx = len(slot_scores) // 2
            mid_slot = slot_scores[mid_idx]
            mid_dt = mid_slot.dt
            mid_gochara = mid_slot.gochara
            mid_ctx = build_context(mid_dt, location, person)
            panchang = build_panchang(mid_dt, mid_ctx.moon_constellation, mid_ctx.lunar_day, mid_ctx.weekday)
            panchang_score = panchang.yoga_score + panchang.karana_score

        raw_composites: list[float] = []
        for s in slot_scores:
            effective_dasha = s.dasha_b + sade_sati_penalty + special.overall_penalty + s.sandhi_penalty

            composite = compute_composite_score(
                category=category,
                rule_score=s.rule_score,
                shadbala_bonus=sha_centered + lagna_lord_bonus + divisional_bonus,
                gochara_score=s.gochara,
                dasha_bonus=effective_dasha,
                yoga_score=yoga_score,
                ashtakavarga_bonus=s.avarga + s.panchang_s,
                tara_score=s.tara_score,
                chandra_bala_score=s.chandra_bala_score,
                avastha_score=s.avastha_score,
                pushkara_bonus_score=s.pushkara_bonus_score,
                sudarshana_score=s.sudarshana_score,
                jaimini_score=jaimini_score,
                arudha_score=arudha_score,
                gulika_penalty=gulika_pen,
                badhaka_penalty=badhaka_pen,
            )
            raw_composites.append(composite)

        import math

        normalized: list[float] = []
        if raw_composites:
            sorted_c = sorted(raw_composites)
            median_c = sorted_c[len(sorted_c) // 2]
            # avoid division by zero
            score_range = max(sorted_c[-1] - sorted_c[0], 1.0)

            for c in raw_composites:
                # Absolute S-curve mapping bounds raw scores to ~ [-3.0, 3.0]
                abs_norm = 3.0 * math.tanh(c / 4.0)

                # Relative mapping forces the period's local minimum/maximum to stretch across [-3, 3]
                rel_norm = ((c - median_c) / score_range) * 6.0
                rel_norm = max(-3.0, min(3.0, rel_norm))

                # Hybrid: heavily absolute to preserve true astrological signal,
                # with minimal relative weight for local variation
                hybrid = (abs_norm * 0.85) + (rel_norm * 0.15)
                normalized.append(round(hybrid, 3))

        composite_slots: list[tuple[_SlotScore, float]] = [
            (slot_scores[i], normalized[i]) for i in range(len(slot_scores))
        ]

        step_min = time_range.step_minutes
        step_td = timedelta(minutes=step_min)

        def _flush(start, end, scores, slots):
            avg_score = sum(scores) / len(scores)
            if avg_score > 1.5:
                nature = "good"
            elif avg_score < -1.5:
                nature = "bad"
            else:
                nature = "neutral"

            all_events: list[str] = []
            for sl in slots:
                all_events.extend(sl.active_events)
            unique_events = list(dict.fromkeys(all_events))

            avg_gochara = sum(sl.gochara for sl in slots) / len(slots)
            avg_dasha = sum(sl.dasha_b for sl in slots) / len(slots)
            avg_avarga = sum(sl.avarga for sl in slots) / len(slots)
            avg_rule = sum(sl.rule_score for sl in slots) / len(slots)

            w_maha, w_antar, w_prat = dasha_engine.active_full_at(start)
            if w_maha and w_antar and w_prat:
                dasha_str = f"{w_maha.planet}/{w_antar.planet}/{w_prat.planet}"
            elif w_maha and w_antar:
                dasha_str = f"{w_maha.planet}/{w_antar.planet}"
            elif w_maha:
                dasha_str = w_maha.planet
            else:
                dasha_str = ""

            dur = max((end - start).total_seconds() / 60, step_min)
            return PredictionWindow(
                start=start,
                end=end,
                nature=nature,
                composite_score=round(avg_score, 3),
                rank=rank_window(round(avg_score, 3), dur),
                duration_minutes=dur,
                active_events=unique_events if unique_events else ["(background)"],
                dasha_active=[dasha_str] if dasha_str else [],
                yogas_active=[y["name"] for y in active_yogas],
                gochara_score=round(avg_gochara, 3),
                shadbala_score=round(sha_centered, 3),
                dasha_bonus=round(avg_dasha, 3),
                yoga_score=round(yoga_score, 3),
                ashtakavarga_bonus=round(avg_avarga, 3),
                rule_score=round(avg_rule, 3),
            )

        max_window_hours = 12
        max_slots_per_window = max(1, int((max_window_hours * 60) / step_min))

        prediction_windows: list[PredictionWindow] = []
        if composite_slots:
            cur_start = composite_slots[0][0].dt
            cur_scores = [composite_slots[0][1]]
            cur_slots = [composite_slots[0][0]]

            for i in range(1, len(composite_slots)):
                slot, score = composite_slots[i]
                prev_slot, prev_score = composite_slots[i - 1]

                time_gap = (slot.dt - prev_slot.dt).total_seconds() / 60
                window_full = len(cur_scores) >= max_slots_per_window
                day_boundary = slot.dt.date() != cur_start.date()

                if window_full or day_boundary or time_gap > step_min * 1.5:
                    prediction_windows.append(
                        _flush(cur_start, prev_slot.dt + step_td, cur_scores, cur_slots)
                    )
                    cur_start = slot.dt
                    cur_scores = [score]
                    cur_slots = [slot]
                else:
                    cur_scores.append(score)
                    cur_slots.append(slot)

            prediction_windows.append(
                _flush(cur_start, composite_slots[-1][0].dt + step_td, cur_scores, cur_slots)
            )

        prediction_windows.sort(key=lambda x: -x.rank)

        overall_score = 0.0
        if prediction_windows:
            overall_score = round(
                sum(w.composite_score for w in prediction_windows) / len(prediction_windows), 2
            )

        narrative = _build_narrative(
            category=category,
            maha=maha,
            antar=antar,
            active_yogas=active_yogas,
            gochara_score=mid_gochara,
            shadbala=shadbala,
            overall_score=overall_score,
            sade_sati=sade_sati,
            special=special,
            panchang=panchang,
        )

        return LifePrediction(
            category=category,
            person_name=person.name,
            time_range_start=time_range.start,
            time_range_end=time_range.end,
            natal_lagna=n_lagna,
            natal_moon_sign=n_moon,
            active_dashas=active_dasha_info,
            yogas=active_yogas,
            shadbala=shadbala,
            gochara_score=mid_gochara,
            sade_sati=sade_sati_dict,
            special_conditions=special.summary(),
            panchang_score=panchang_score,
            windows=prediction_windows,
            top_windows=prediction_windows[:5],
            overall_period_score=overall_score,
            narrative=narrative,
        )


def _build_narrative(
    category: str,
    maha,
    antar,
    active_yogas: list[dict],
    gochara_score: float,
    shadbala: dict[str, float],
    overall_score: float,
    sade_sati=None,
    special=None,
    panchang=None,
) -> str:
    parts = []

    if maha:
        parts.append(f"{maha.planet} Mahadasha is active")
        if antar:
            parts.append(f"with {antar.planet} Antardasha")
        parts.append(".")

    if sade_sati and sade_sati.currently_active:
        phase = sade_sati.current_phase
        parts.append(
            f"⚠ Sade Sati is active ({phase.phase} phase, Saturn in {phase.saturn_sign}) — "
            f"expect karmic challenges and restructuring."
        )
    elif sade_sati and sade_sati.dhaiya_active:
        parts.append(f"Shani Dhaiya is active (Saturn in {sade_sati.dhaiya_sign}) — minor obstacles possible.")

    if special:
        if special.kaal_sarp_dosha:
            parts.append(f"⚠ Kaal Sarp Dosha present ({special.kaal_sarp_type}) — amplified karmic intensity.")
        if special.mangal_dosha:
            parts.append("Mangal Dosha present — caution in relationships and partnerships.")
        combust = [p for p, r in special.combustion.items() if r.combust]
        if combust:
            parts.append(f"Planets combust (near Sun): {', '.join(combust)}.")
        retro = [p for p, r in special.retrograde.items() if r.retrograde]
        if retro:
            parts.append(f"Retrograde planets (intensified/internalized): {', '.join(retro)}.")

    if panchang:
        if panchang.yoga_nature == "good":
            parts.append(f"Panchang Yoga '{panchang.yoga_name}' is auspicious.")
        elif panchang.yoga_nature == "bad":
            parts.append(f"Panchang Yoga '{panchang.yoga_name}' is inauspicious — avoid major decisions.")
        if panchang.karana_name == "Vishti":
            parts.append("Vishti Karana (Bhadra) is active — avoid new beginnings.")

    if active_yogas:
        yoga_names = ", ".join(y["name"] for y in active_yogas[:3])
        parts.append(f"Active natal yogas: {yoga_names}.")

    if gochara_score > 2:
        parts.append("Planetary transits are strongly favourable.")
    elif gochara_score > 0:
        parts.append("Planetary transits are mildly favourable.")
    elif gochara_score < -2:
        parts.append("Planetary transits are unfavourable — caution advised.")
    else:
        parts.append("Planetary transits are mixed.")

    if overall_score > 5:
        parts.append(f"Overall outlook for {category} is excellent (score: {overall_score}).")
    elif overall_score > 2:
        parts.append(f"Overall outlook for {category} is positive (score: {overall_score}).")
    elif overall_score > 0:
        parts.append(f"Overall outlook for {category} is moderate (score: {overall_score}).")
    else:
        parts.append(f"This period may present challenges for {category}.")

    return " ".join(parts)
