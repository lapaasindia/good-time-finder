"""
Astrology Report Generator
Aggregates all astrological factors into a comprehensive report dictionary.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math

from app.core.models import Person, GeoLocation
from app.astrology.calculations import (
    natal_lagna, natal_moon_sign, planet_houses, planet_signs,
    moon_constellation, _longitude_to_sign
)
from app.astrology.shadbala import shadbala_summary, benefic_strength_score, lagna_lord_strength
from app.astrology.yogas import detect_all_yogas
from app.astrology.extra_yogas import detect_all_extra_yogas
from app.astrology.special_conditions import compute_special_conditions, get_raw_longitudes
from app.astrology.lal_kitab import get_lal_kitab_remedies
from app.astrology.houses_info import HOUSE_DATA
from app.astrology.planets_info import PLANET_DATA
from app.astrology.personality_info import ZODIAC_PROFILES
from app.astrology.dasha import compute_mahadashas, compute_antardashas, compute_pratyantardashas
from app.astrology.sade_sati import compute_sade_sati
from app.astrology.gochara import gochara_score, _house_from_sign
from app.astrology.calculations import build_context



from app.astrology.drishti import compute_aspects
from app.astrology.avasthas import compute_all_avasthas
from app.astrology.nadi import compute_nadi_linkages
from app.astrology.jaimini import compute_chara_karakas
from app.astrology.remedies_pro import prescribe_gemstones, prescribe_rudraksha, prescribe_astro_vastu
from app.services.synthesis_engine import SynthesisEngine

def generate_full_report_data(person: Person, current_dt: datetime = None) -> dict:
    """
    Generates a massive dictionary containing ALL astrological data for the person,
    ready to be serialized to JSON or rendered into a PDF.
    """
    if current_dt is None:
        current_dt = datetime.now(timezone.utc)

    # 1. Core Calculations
    natal_longs = get_raw_longitudes(person.birth_datetime)
    n_lagna = natal_lagna(person)
    n_moon = natal_moon_sign(person)
    n_nakshatra = moon_constellation(person.birth_datetime, person.birth_location)
    
    n_planet_signs = planet_signs(person.birth_datetime, person.birth_location)
    n_planet_houses = planet_houses(person.birth_datetime, person.birth_location)
    
    # 2. Planetary Strength & States
    shadbala = shadbala_summary(n_planet_signs, n_planet_houses)
    drishti = compute_aspects(n_planet_houses)
    avasthas = compute_all_avasthas(natal_longs)
    
    # 3. Yogas & Special Modifiers
    yogas = detect_all_yogas(n_planet_houses, n_planet_signs, n_lagna)
    extra_yogas = detect_all_extra_yogas(n_planet_houses, n_planet_signs, n_lagna)
    all_yogas = yogas + extra_yogas
    special = compute_special_conditions(person.birth_datetime, n_planet_houses, n_planet_signs, n_lagna)
    
    # 4. Advanced Systems (Jaimini & Nadi)
    nadi_links = compute_nadi_linkages(n_planet_houses)
    chara_karakas = compute_chara_karakas(natal_longs)

    # 5. Core Synthesis Engine (The "Jury")
    synth_engine = SynthesisEngine(
        planet_houses=n_planet_houses,
        planet_signs=n_planet_signs,
        lagna=n_lagna,
        shadbala=shadbala,
        drishti=drishti,
        avasthas=avasthas,
        nadi_links=nadi_links,
        chara_karakas=chara_karakas
    )
    synthesis_outcomes = synth_engine.run_all()
    
    # 6. Comprehensive Remedies
    remedies_lal_kitab = get_lal_kitab_remedies(n_planet_houses)
    remedies_gems = prescribe_gemstones(n_planet_houses, n_planet_signs, n_lagna, shadbala)
    remedies_rudraksha = prescribe_rudraksha(shadbala)
    remedies_vastu = prescribe_astro_vastu(shadbala)
    
    # 7. Dasha Timeline & Sade Sati & Transits
    mahas = compute_mahadashas(person.birth_datetime, n_nakshatra, natal_longs.get("Moon", 0.0))
    current_maha = None
    current_antar = None
    dasha_list = []
    
    for m in mahas:
        if m.end > current_dt:
            # only collect current and future mahadashas
            dasha_list.append({"planet": m.planet, "start": m.start.strftime("%Y-%m-%d"), "end": m.end.strftime("%Y-%m-%d")})
            
        if m.start <= current_dt <= m.end:
            current_maha = m
            antars = compute_antardashas(m)
            for a in antars:
                if a.start <= current_dt <= a.end:
                    current_antar = a
                    break

    sade_sati = compute_sade_sati(n_moon, current_dt)
    
    # Transit (Gochara) for today
    ctx = build_context(current_dt, person.birth_location, person)
    current_signs = ctx.planet_signs
    from app.astrology.gochara import _house_from_sign, gochara_score
    transit_scores = {}
    gochara_results = gochara_score(current_signs, n_moon)
    for p, sign in current_signs.items():
        if p in ["Lagna", "Uranus", "Neptune", "Pluto"]:
            continue
        h = _house_from_sign(n_moon, sign)
        transit_scores[p] = {"house_from_moon": h, "score": gochara_results.get(p, 0.0)}


    # 8. Personality Profile
    profile = ZODIAC_PROFILES.get(n_lagna)
    moon_profile = ZODIAC_PROFILES.get(n_moon)

    # Assemble output
    report = {
        "personal_info": {
            "name": person.name,
            "dob": person.birth_datetime.strftime("%d %b %Y, %I:%M %p"),
            "place": f"{person.birth_location.latitude}, {person.birth_location.longitude}",
            "lagna": n_lagna,
            "moon_sign": n_moon,
            "nakshatra": n_nakshatra,
        },
        "planetary_positions": [],
        "houses_info": [],
        "personality": {
            "lagna_based": {
                "nature_en": profile.nature_en if profile else "",
                "nature_hi": profile.nature_hi if profile else "",
                "career_en": profile.career_en if profile else "",
                "career_hi": profile.career_hi if profile else "",
                "health_en": profile.health_en if profile else "",
                "health_hi": profile.health_hi if profile else "",
                "relationship_en": profile.relationship_en if profile else "",
                "relationship_hi": profile.relationship_hi if profile else "",
            }
        },
        "synthesis": [],
        "shadbala": shadbala,
        "yogas": [],
        "doshas": special.summary(),
        "remedies": {
            "lal_kitab": [],
            "gemstones": remedies_gems,
            "rudraksha": remedies_rudraksha,
            "vastu": remedies_vastu
        },
        "current_dasha": {
            "maha": current_maha.planet if current_maha else "Unknown",
            "antar": current_antar.planet if current_antar else "Unknown",
        },
        "dasha_list": dasha_list[:5], # Next 5 Mahadashas
        "sade_sati": sade_sati.model_dump() if hasattr(sade_sati, "model_dump") else sade_sati.dict() if hasattr(sade_sati, "dict") else sade_sati,
        "transits": transit_scores
    }

    # Fill Synthesis Outcomes
    for syn in synthesis_outcomes:
        report["synthesis"].append({
            "domain_en": syn.domain_en,
            "domain_hi": syn.domain_hi,
            "summary_en": syn.summary_en,
            "summary_hi": syn.summary_hi,
            "key_factors_en": syn.key_factors_en,
            "key_factors_hi": syn.key_factors_hi,
        })

    # Fill Planetary Positions & Meanings
    for p, sign in n_planet_signs.items():
        house_num = n_planet_houses.get(p, 1)
        p_info = PLANET_DATA.get(p)
        strength = shadbala.get(p, 1.0)
        av = avasthas.get(p)
        
        report["planetary_positions"].append({
            "planet": p,
            "sign": sign,
            "house": house_num,
            "strength": round(strength, 2),
            "avastha_en": av.state_en if av else "",
            "avastha_hi": av.state_hi if av else "",
            "nature_en": p_info.nature_en if p_info else "",
            "nature_hi": p_info.nature_hi if p_info else "",
            "significations_en": p_info.significations_en if p_info else "",
            "significations_hi": p_info.significations_hi if p_info else "",
        })

    # Fill Houses Info
    for h in range(1, 13):
        h_info = HOUSE_DATA.get(h)
        occupants = [p for p, house in n_planet_houses.items() if house == h]
        
        # Aspects on this house
        h_aspects = drishti[0].get(h, set())
        
        report["houses_info"].append({
            "house": h,
            "name_en": h_info.name_en if h_info else f"House {h}",
            "name_hi": h_info.name_hi if h_info else f"भाव {h}",
            "domain_en": h_info.domain_en if h_info else "",
            "domain_hi": h_info.domain_hi if h_info else "",
            "body_parts_en": h_info.body_parts_en if h_info else "",
            "body_parts_hi": h_info.body_parts_hi if h_info else "",
            "occupants": occupants,
            "aspected_by": list(h_aspects)
        })

    # Fill Yogas
    for y in all_yogas:
        if y.present:
            report["yogas"].append({
                "name": y.name,
                "description": y.description,
                "score": y.strength
            })

    # Fill Lal Kitab
    for lk in remedies_lal_kitab:
        report["remedies"]["lal_kitab"].append({
            "planet": lk.planet,
            "house": lk.house,
            "effect_en": lk.effect_en,
            "effect_hi": lk.effect_hi,
            "remedies_en": lk.remedies_en,
            "remedies_hi": lk.remedies_hi,
            "donate_en": lk.donate_en,
            "donate_hi": lk.donate_hi,
            "avoid_en": lk.avoid_en,
            "avoid_hi": lk.avoid_hi,
        })

    return report
