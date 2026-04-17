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
from app.astrology.bhrigu import calculate_bhrigu_bindu, bhrigu_transit_score
from app.astrology.kp import kp_score, true_kp_cuspal_score
from app.astrology.double_transit import double_transit_score
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
from app.core.ranking import compute_composite_score, batch_composite_scores, get_weights, rank_window
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
    tara_score: float = 0.0
    chandra_bala_score: float = 0.0
    avastha_score: float = 0.0
    pushkara_bonus_score: float = 0.0
    sudarshana_score: float = 0.0
    sandhi_penalty: float = 0.0
    bhrigu_bonus: float = 0.0
    kp_score: float = 0.0
    kp_cuspal_score: float = 0.0
    double_transit: float = 0.0
    panchang_score: float = 0.0
    confidence: float = 0.0


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
    jaimini_score: float = 0.0
    arudha_score: float = 0.0
    gulika_penalty: float = 0.0
    badhaka_penalty: float = 0.0
    divisional_scores: dict[str, float] = field(default_factory=dict)
    bhrigu_bonus: float = 0.0
    kp_score: float = 0.0
    kp_cuspal_score: float = 0.0
    double_transit: float = 0.0
    # Phase 2: static natal KP anchors (for chart signature vs per-slot kp_score/kp_cuspal_score)
    kp_natal_score: float = 0.0
    kp_natal_cuspal: float = 0.0
    # Phase 6: domain static scores & confidences
    domain_static_scores: dict[str, float] = field(default_factory=dict)
    domain_confidences: dict[str, float] = field(default_factory=dict)


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
        divisional_bonus = (d9_score * 0.3 + d10_score * 0.3 + d2_score * 0.15 + d7_score * 0.1 + vimsopaka_score * 0.15) * 0.2  # Scaled down

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
        # Disabled as it drops accuracy based on previous backtests
        # yoga_activation = _yoga_dasha_activation(
        #     active_yogas,
        #     maha.planet if maha else None,
        #     antar.planet if antar else None,
        # )
        # yoga_score = round(yoga_score * yoga_activation, 3)
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

        lagna_lord_bonus = lagna_lord_strength(n_lagna, shadbala, natal_p_houses) * 0.15  # Scaled down to prevent static chart bias

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
            bhrigu_bonus: float
            kp_score: float
            kp_cuspal_score: float
            double_transit: float
            gochara_house_specific: float
            planet_focus: float
            active_events: list[str]
            nature: str

        # Bhrigu and KP
        natal_longs = get_raw_longitudes(person.birth_datetime)
        moon_long = natal_longs.get("Moon", 0.0)
        rahu_long = natal_longs.get("Rahu", 0.0)
        bb_long = calculate_bhrigu_bindu(moon_long, rahu_long)
        natal_kp_score = kp_score(natal_longs, n_lagna, category)
        natal_kp_cuspal = true_kp_cuspal_score(
            category=category,
            birth_dt=person.birth_datetime,
            lat=person.birth_location.latitude,
            lon=person.birth_location.longitude,
            natal_longs=natal_longs,
            natal_houses=natal_p_houses
        )
        # Natal Bhrigu score at birth (transits over BB)
        natal_bhrigu_score = bhrigu_transit_score(bb_long, natal_longs)
        # Natal double transit (Jupiter + Saturn vs natal positions)
        natal_double_transit = double_transit_score(category, natal_longs, natal_p_houses, n_lagna)

        # Phase 3 specific mappings
        CATEGORY_HOUSES = {
            "career": {10, 6, 11},
            "finance": {2, 11},
            "marriage": {7},
            "relationships": {5, 7},
            "health": {1, 6},
            "education": {4, 5, 9},
            "children": {5},
            "property": {4},
            "spirituality": {9, 12},
            "legal": {6, 8, 12},
            "travel": {3, 9, 12},
            "business": {7, 10, 11},
            "accidents": {8, 12},
            "fame": {10, 11},
            "general": {1, 9, 10}
        }
        
        CATEGORY_PRIMARY_PLANET = {
            "career": "Saturn",
            "finance": "Jupiter",
            "marriage": "Venus",
            "relationships": "Venus",
            "health": "Sun",
            "education": "Mercury",
            "children": "Jupiter",
            "property": "Mars",
            "spirituality": "Ketu",
            "legal": "Saturn",
            "travel": "Rahu",
            "business": "Mercury",
            "accidents": "Mars",
            "fame": "Sun",
            "general": "Jupiter"
        }
        
        relevant_houses = CATEGORY_HOUSES.get(category, {1})
        primary_planet = CATEGORY_PRIMARY_PLANET.get(category, "Jupiter")
        # Static planet focus for the category based on natal shadbala
        planet_focus = shadbala.get(primary_planet, 1.0) - 1.0

        slot_scores: list[_SlotScore] = []

        from app.astrology.calculations import moon_constellation
        natal_nakshatra = moon_constellation(person.birth_datetime, person.birth_location)

        for dt in time_points:
            ctx = build_context(dt, location, person)
            current_p_signs = ctx.planet_signs

            # Retrograde detection for transit planets
            transit_speeds = get_speeds(dt)
            retro_planets = {p for p, spd in transit_speeds.items() if spd < 0}

            # ── Tara Bala (Nakshatra transit strength) ──
            transit_nakshatra = moon_constellation(dt, location)
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
            from app.astrology.gochara import house_specific_gochara_score
            gochara_house_specific = house_specific_gochara_score(current_p_signs, n_moon, relevant_houses)
            
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

            bhrigu_score = bhrigu_transit_score(bb_long, transit_longitudes)
            dt_score = double_transit_score(category, transit_longitudes, natal_p_houses, n_lagna)

            # Phase 2: KP scores computed per-slot using transit data
            # kp_score uses transit Moon sub-lord (changes every few hours)
            transit_kp = kp_score(transit_longitudes, n_lagna, category)
            # true_kp_cuspal_score computes ascendant cusp from current dt (rotates ~4 min)
            # and checks transit cusp sub-lord's star-lord placement in natal houses
            try:
                transit_kp_cuspal = true_kp_cuspal_score(
                    category=category,
                    birth_dt=dt,
                    lat=location.latitude,
                    lon=location.longitude,
                    natal_longs=transit_longitudes,
                    natal_houses=natal_p_houses,
                )
            except Exception:
                transit_kp_cuspal = natal_kp_cuspal

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
                bhrigu_bonus=bhrigu_score,
                kp_score=transit_kp,
                kp_cuspal_score=transit_kp_cuspal,
                double_transit=dt_score,
                gochara_house_specific=gochara_house_specific,
                planet_focus=planet_focus,
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

        feature_rows: list[list[float]] = []
        for s in slot_scores:
            effective_dasha = s.dasha_b + sade_sati_penalty + special.overall_penalty
            # Phase 1: panchang is an independent feature; Phase 3 adds 2 placeholders
            feature_rows.append([
                s.rule_score, sha_centered, s.gochara, effective_dasha,
                yoga_score, s.avarga, s.panchang_s, s.tara_score,
                s.chandra_bala_score, s.avastha_score, s.pushkara_bonus_score,
                s.sudarshana_score, jaimini_score, arudha_score,
                gulika_pen, badhaka_pen, s.bhrigu_bonus,
                s.kp_score, s.kp_cuspal_score, s.double_transit,
                s.gochara_house_specific, s.planet_focus,  # gochara_house_specific, planet_focus (Phase 3)
            ])
        raw_composites = batch_composite_scores(category, feature_rows)

        import math

        normalized: list[float] = []
        if raw_composites:
            for c in raw_composites:
                # Phase 6: Pure tanh normalization against SCALE=2.0
                # raw_composites from batch_composite_scores are not clamped anymore?
                # Actually, batch_composite_scores clamps to [-3,3]. Let's remove the clamp in ranking.py
                # or just use the raw score. We'll use tanh to gently map large values.
                # We will map `c` through 3.0 * tanh(c / 2.0).
                norm = 3.0 * math.tanh(c / 2.0)
                normalized.append(round(norm, 3))

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
            avg_tara = sum(sl.tara_score for sl in slots) / len(slots)
            avg_chandra = sum(sl.chandra_bala_score for sl in slots) / len(slots)
            avg_avastha = sum(sl.avastha_score for sl in slots) / len(slots)
            avg_pushkara = sum(sl.pushkara_bonus_score for sl in slots) / len(slots)
            avg_sudarshana = sum(sl.sudarshana_score for sl in slots) / len(slots)
            avg_sandhi = sum(sl.sandhi_penalty for sl in slots) / len(slots)
            avg_bhrigu = sum(sl.bhrigu_bonus for sl in slots) / len(slots)
            avg_kp = sum(sl.kp_score for sl in slots) / len(slots)
            avg_kp_cuspal = sum(sl.kp_cuspal_score for sl in slots) / len(slots)
            avg_double_transit = sum(sl.double_transit for sl in slots) / len(slots)
            avg_panchang = sum(sl.panchang_s for sl in slots) / len(slots)

            # Phase 6.4: Confidence = fraction of non-zero signals agreeing with composite sign
            feature_vals = [
                avg_gochara, avg_dasha, avg_avarga, avg_rule,
                avg_tara, avg_chandra, avg_avastha, avg_pushkara,
                avg_sudarshana, avg_sandhi, avg_bhrigu, avg_kp,
                avg_kp_cuspal, avg_double_transit, avg_panchang,
                sha_centered, yoga_score,
            ]
            nonzero = [v for v in feature_vals if abs(v) > 1e-6]
            if nonzero and abs(avg_score) > 1e-6:
                sign_of_composite = 1.0 if avg_score > 0 else -1.0
                agreeing = sum(1 for v in nonzero if (v > 0) == (sign_of_composite > 0))
                window_confidence = round(agreeing / len(nonzero), 3)
            else:
                window_confidence = 0.0

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
                tara_score=round(avg_tara, 3),
                chandra_bala_score=round(avg_chandra, 3),
                avastha_score=round(avg_avastha, 3),
                pushkara_bonus_score=round(avg_pushkara, 3),
                sudarshana_score=round(avg_sudarshana, 3),
                sandhi_penalty=round(avg_sandhi, 3),
                bhrigu_bonus=round(avg_bhrigu, 3),
                kp_score=round(avg_kp, 3),
                kp_cuspal_score=round(avg_kp_cuspal, 3),
                double_transit=round(avg_double_transit, 3),
                panchang_score=round(avg_panchang, 3),
                confidence=window_confidence,
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
            windows=prediction_windows,
        )

        # Phase 6: Compute domain static scores for current category
        from app.core.domain_scorer import score_domain, ScoringContext
        from app.astrology.drishti import compute_aspects
        from app.astrology.avasthas import compute_all_avasthas
        from app.astrology.nadi import compute_nadi_linkages

        natal_drishti = compute_aspects(natal_p_houses)
        natal_avasthas = compute_all_avasthas(natal_longitudes)
        natal_nadi_links = compute_nadi_linkages(natal_p_houses)
        scoring_ctx = ScoringContext(
            natal_houses=natal_p_houses,
            natal_signs=natal_p_signs,
            lagna=n_lagna,
            shadbala=shadbala,
            drishti_house=natal_drishti[0] if isinstance(natal_drishti, tuple) else natal_drishti,
            drishti_planet=natal_drishti[1] if isinstance(natal_drishti, tuple) else {},
            avasthas=natal_avasthas,
            nadi_links=natal_nadi_links,
            chara_karakas=chara_karakas,
            kp_natal_cuspal=natal_kp_cuspal,
            kp_natal_score=natal_kp_score,
            bhrigu_bonus=natal_bhrigu_score,
            active_maha=maha.planet if maha else None,
            active_antar=antar.planet if antar else None,
        )

        domain_static_scores: dict[str, float] = {}
        domain_confidences: dict[str, float] = {}
        try:
            ds = score_domain(category, scoring_ctx)
            domain_static_scores[category] = round(ds.score, 3)
            domain_confidences[category] = ds.confidence
        except Exception:
            domain_static_scores[category] = 0.0
            domain_confidences[category] = 0.0

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
            jaimini_score=jaimini_score,
            arudha_score=arudha_score,
            gulika_penalty=gulika_pen,
            badhaka_penalty=badhaka_pen,
            divisional_scores={"d9": d9_score, "d10": d10_score, "d2": d2_score, "d7": d7_score, "vimsopaka": vimsopaka_score},
            bhrigu_bonus=round(natal_bhrigu_score, 3),
            kp_score=round(natal_kp_score, 3),
            kp_cuspal_score=round(natal_kp_cuspal, 3),
            double_transit=round(natal_double_transit, 3),
            kp_natal_score=round(natal_kp_score, 3),
            kp_natal_cuspal=round(natal_kp_cuspal, 3),
            domain_static_scores=domain_static_scores,
            domain_confidences=domain_confidences,
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
    windows: list[PredictionWindow] | None = None,
) -> str:
    category_labels = {
        "general": "overall life decisions",
        "travel": "travel and movement",
        "marriage": "marriage and partnership",
        "career": "career and professional decisions",
        "finance": "money and financial choices",
        "health": "health and recovery",
        "education": "study and skill-building",
        "property": "property and home matters",
        "children": "children and family planning",
        "spirituality": "inner work and spiritual practice",
        "legal": "legal and dispute-related matters",
        "fame": "visibility and public recognition",
        "business": "business and commercial decisions",
        "relationships": "relationships and emotional connection",
        "accidents": "risk management and physical caution",
    }
    category_actions = {
        "general": "important conversations, planning, and steady decisions",
        "travel": "bookings, logistics, applications, and movement plans",
        "marriage": "important relationship talks, introductions, or commitment planning",
        "career": "interviews, proposals, launches, presentations, and work conversations",
        "finance": "budgeting, negotiations, purchases, and practical money planning",
        "health": "check-ins, treatment planning, rest, and sustainable routines",
        "education": "study, applications, writing, and exams",
        "property": "home decisions, property paperwork, and long-term planning",
        "children": "family conversations, planning, and nurturing routines",
        "spirituality": "reflection, retreat, practice, and inner reset",
        "legal": "documents, response strategy, and careful advice-taking",
        "fame": "public visibility, branding, and speaking opportunities",
        "business": "sales, partnerships, negotiations, and execution",
        "relationships": "communication, repair, and expectation-setting",
        "accidents": "slowing down, travel caution, and risk reduction",
    }
    planet_focus = {
        "Sun": "confidence, visibility, leadership, and authority",
        "Moon": "emotions, home life, habits, and mental steadiness",
        "Mars": "drive, courage, conflict, and action",
        "Mercury": "learning, writing, deals, analysis, and communication",
        "Jupiter": "growth, learning, mentors, wisdom, and long-term opportunity",
        "Venus": "relationships, comfort, design, pleasure, and agreement",
        "Saturn": "discipline, delay, responsibility, and long-term structure",
        "Rahu": "ambition, novelty, foreign links, and restless desire",
        "Ketu": "detachment, specialization, and stepping back from noise",
    }

    def _friendly_dt(dt: datetime) -> str:
        return dt.strftime("%d %b %Y %I:%M %p")

    def _overall_sentence() -> str:
        label = category_labels.get(category, category)
        if overall_score >= 1.5:
            return f"{label.capitalize()} look especially strong in this range, so well-prepared action has a better than usual chance of landing well."
        if overall_score >= 0.5:
            return f"{label.capitalize()} look supportive overall in this range, especially if you stay steady and avoid unnecessary drama."
        if overall_score >= -0.5:
            return f"{label.capitalize()} look mixed in this range, so selectivity and timing matter more than speed."
        if overall_score >= -1.5:
            return f"{label.capitalize()} look somewhat demanding in this range, so it is better to move carefully than to force results."
        return f"{label.capitalize()} look quite heavy in this range, so use the period more for protection, repair, and cleaner judgment than expansion."

    def _timing_cycle_sentence() -> str:
        if not maha:
            return ""
        maha_focus = planet_focus.get(maha.planet, "major life themes")
        if antar:
            antar_focus = planet_focus.get(antar.planet, "a shorter sub-theme")
            return (
                f"The main timing cycle is {maha.planet}, with {antar.planet} as the active sub-cycle. "
                f"In plain English, {maha.planet} is turning up {maha_focus}, while {antar.planet} adds extra focus on {antar_focus}."
            )
        return (
            f"The main timing cycle is {maha.planet}. "
            f"This tends to make {maha_focus} more central than usual."
        )

    def _transit_sentence() -> str:
        if gochara_score >= 1.5:
            return "Current transits are strongly supportive, so the environment around you is helping more than usual."
        if gochara_score >= 0.5:
            return "Current transits are mildly supportive, which helps progress if you stay practical."
        if gochara_score >= -0.5:
            return "Current transits are mixed, so external conditions may feel changeable even when the plan is sound."
        if gochara_score >= -1.5:
            return "Current transits are on the heavier side, so delays, mood swings, or mixed signals are more likely than usual."
        return "Current transits are quite heavy, so leave extra margin and avoid decisions made only from pressure."

    def _saturn_sentence() -> str:
        if sade_sati and sade_sati.currently_active and sade_sati.current_phase:
            phase = sade_sati.current_phase
            return (
                f"Sade Sati is active in its {phase.phase.lower()} phase, which usually feels like a Saturn season: "
                "slower progress, stronger reality checks, and a bigger need for patience and structure."
            )
        if sade_sati and sade_sati.dhaiya_active:
            return "Shani Dhaiya is active, so this is a better phase for disciplined pacing than impulsive expansion."
        return ""

    def _special_sentence() -> str:
        if not special:
            return ""
        lines: list[str] = []
        if special.kaal_sarp_dosha:
            lines.append("the chart can move through sharper highs and lows than average")
        if special.mangal_dosha:
            lines.append("relationships and reactive decisions benefit from extra patience")
        combust = [planet for planet, result in special.combustion.items() if result.combust]
        if combust:
            lines.append(f"{', '.join(combust[:2])} may act less directly because they are too close to the Sun")
        if not lines:
            return ""
        return "Birth-chart sensitivity is a bit higher here: " + "; ".join(lines) + "."

    def _panchang_sentence() -> str:
        if not panchang:
            return ""
        if panchang.yoga_nature == "good" and panchang.karana_nature != "bad":
            return f"The day-quality factors are supportive right now, so routine decisions may move more smoothly than expected."
        if panchang.yoga_nature == "bad" or panchang.karana_name == "Vishti":
            return f"The day-quality factors are a little rough right now, so double-check timing and leave buffer for friction."
        return ""

    def _natal_support_sentence() -> str:
        ordered = sorted(shadbala.items(), key=lambda item: item[1], reverse=True)
        strongest = [planet for planet, _ in ordered[:2]]
        strong_line = ""
        if strongest:
            strong_line = f"Stronger natal support comes from {', '.join(strongest)}, so those themes are easier to access under pressure."
        if active_yogas:
            yoga_names = ", ".join(y["name"] for y in active_yogas[:2])
            if strong_line:
                return strong_line + f" Helpful natal combinations in the background include {yoga_names}."
            return f"Helpful natal combinations in the background include {yoga_names}."
        return strong_line

    def _window_sentence() -> str:
        if not windows:
            return ""
        best = max(windows, key=lambda item: item.composite_score)
        worst = min(windows, key=lambda item: item.composite_score)
        parts: list[str] = []
        if best.composite_score > 0:
            parts.append(
                f"The best window in this range is {_friendly_dt(best.start)} to {_friendly_dt(best.end)}, "
                f"which is better suited for {category_actions.get(category, 'important decisions')}."
            )
        if worst.composite_score < -0.8 and worst.start != best.start:
            parts.append(
                f"The touchier patch is {_friendly_dt(worst.start)} to {_friendly_dt(worst.end)}, "
                "so use extra patience there and avoid forcing outcomes."
            )
        return " ".join(parts)

    parts = [
        _overall_sentence(),
        _timing_cycle_sentence(),
        _transit_sentence(),
        _saturn_sentence(),
        _special_sentence(),
        _panchang_sentence(),
        _natal_support_sentence(),
        _window_sentence(),
    ]
    return " ".join(part.strip() for part in parts if part and part.strip())
