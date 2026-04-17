"""
Advanced Remedial Matrix (Gemstones, Rudraksha, Vastu).
Generates highly personalized prescriptions while strictly avoiding harmful combinations.
"""
from __future__ import annotations
from typing import Any

def prescribe_gemstones(
    planet_houses: dict[str, int], 
    planet_signs: dict[str, str], 
    lagna: str, 
    shadbala: dict[str, float]
) -> dict[str, dict[str, str]]:
    """
    Prescribes gemstones based on the Lagna (Ascendant).
    Strict Safety Rules:
    1. NEVER wear a gemstone for the lord of the 6th, 8th, or 12th houses.
    2. NEVER wear a gemstone for a planet placed in the 6th, 8th, or 12th house (unless strong Viparita Raja Yoga).
    3. ONLY wear gemstones for Functional Benefics (Lords of 1, 5, 9) if they are weak in Shadbala.
    """
    # Lagna Lord, 5th Lord, 9th Lord are functional benefics for that Lagna
    from app.astrology.yogas import _lord_of_house
    
    l1 = _lord_of_house(1, lagna, planet_signs)
    l5 = _lord_of_house(5, lagna, planet_signs)
    l9 = _lord_of_house(9, lagna, planet_signs)
    
    l6 = _lord_of_house(6, lagna, planet_signs)
    l8 = _lord_of_house(8, lagna, planet_signs)
    l12 = _lord_of_house(12, lagna, planet_signs)

    bad_lords = {l6, l8, l12}
    bad_houses = {6, 8, 12}
    
    GEM_DATA = {
        "Sun": ("Ruby", "माणिक"),
        "Moon": ("Pearl", "मोती"),
        "Mars": ("Red Coral", "लाल मूंगा"),
        "Mercury": ("Emerald", "पन्ना"),
        "Jupiter": ("Yellow Sapphire", "पुखराज"),
        "Venus": ("Diamond / White Sapphire", "हीरा / सफेद पुखराज"),
        "Saturn": ("Blue Sapphire", "नीलम"),
        "Rahu": ("Hessonite", "गोमेद"),
        "Ketu": ("Cat's Eye", "लहसुनिया")
    }

    prescriptions = {}
    
    for planet in [l1, l5, l9]:
        if not planet:
            continue
        
        # Check safety:
        # 1. Not a lord of 6,8,12 simultaneously (e.g., Mars for Virgo ascendant rules 3 and 8)
        if planet in bad_lords:
            continue
            
        # 2. Not sitting in 6,8,12
        if planet_houses.get(planet) in bad_houses:
            continue
            
        # 3. Assess Shadbala - If it's already very strong (>1.5), no need to boost it excessively
        strength = shadbala.get(planet, 1.0)
        
        reason = f"Lord of {1 if planet == l1 else (5 if planet == l5 else 9)}th house, safe to wear."
        if strength < 1.0:
            status = "Highly Recommended"
            hi_status = "अत्यधिक अनुशंसित"
        elif strength < 1.4:
            status = "Beneficial"
            hi_status = "लाभदायक"
        else:
            status = "Optional (Already Strong)"
            hi_status = "वैकल्पिक (पहले से ही मजबूत)"
            
        gem_en, gem_hi = GEM_DATA.get(planet, ("Unknown", "अज्ञात"))
        prescriptions[planet] = {
            "gem_en": gem_en,
            "gem_hi": gem_hi,
            "status": status,
            "status_hi": hi_status,
            "reason": reason
        }

    return prescriptions

def prescribe_rudraksha(shadbala: dict[str, float]) -> list[dict[str, str]]:
    """
    Recommends Rudrakshas based on the weakest planets in the chart to balance energies.
    """
    RUDRAKSHA_MAP = {
        "Sun": ("1 Mukhi / 12 Mukhi", "1 मुखी / 12 मुखी", "Confidence & Leadership", "आत्मविश्वास और नेतृत्व"),
        "Moon": ("2 Mukhi", "2 मुखी", "Emotional Peace & Focus", "भावनात्मक शांति और ध्यान"),
        "Mars": ("3 Mukhi", "3 मुखी", "Courage & Energy", "साहस और ऊर्जा"),
        "Mercury": ("4 Mukhi", "4 मुखी", "Intellect & Communication", "बुद्धि और संचार"),
        "Jupiter": ("5 Mukhi", "5 मुखी", "Wisdom & Health", "ज्ञान और स्वास्थ्य"),
        "Venus": ("6 Mukhi", "6 मुखी", "Love & Prosperity", "प्रेम और समृद्धि"),
        "Saturn": ("7 Mukhi / 14 Mukhi", "7 मुखी / 14 मुखी", "Discipline & Removing Obstacles", "अनुशासन और बाधाओं को दूर करना"),
        "Rahu": ("8 Mukhi", "8 मुखी", "Focus & Grounding", "ध्यान और स्थिरता"),
        "Ketu": ("9 Mukhi", "9 मुखी", "Spiritual Growth & Intuition", "आध्यात्मिक विकास और अंतर्ज्ञान")
    }

    recommendations = []
    
    # Sort planets by strength (weakest first)
    weak_planets = sorted(shadbala.items(), key=lambda x: x[1])
    
    # Recommend top 2 weakest planets
    for p, strength in weak_planets[:2]:
        if p in RUDRAKSHA_MAP:
            r_en, r_hi, b_en, b_hi = RUDRAKSHA_MAP[p]
            recommendations.append({
                "planet": p,
                "rudraksha_en": r_en,
                "rudraksha_hi": r_hi,
                "benefit_en": f"To balance weak {p}: {b_en}",
                "benefit_hi": f"कमजोर {p} को संतुलित करने के लिए: {b_hi}"
            })
            
    return recommendations

def prescribe_astro_vastu(shadbala: dict[str, float]) -> dict[str, str]:
    """
    Recommends lucky directions for home/office based on the strongest planet.
    """
    DIRECTION_MAP = {
        "Sun": ("East", "पूर्व", "Fame & Authority", "प्रसिद्धि और अधिकार"),
        "Moon": ("North-West", "उत्तर-पश्चिम", "Peace & Movement", "शांति और गति"),
        "Mars": ("South", "दक्षिण", "Energy & Aggression", "ऊर्जा और आक्रामकता"),
        "Mercury": ("North", "उत्तर", "Wealth & Business", "धन और व्यापार"),
        "Jupiter": ("North-East", "ईशान कोण", "Wisdom & Spirituality", "ज्ञान और आध्यात्मिकता"),
        "Venus": ("South-East", "आग्नेय कोण", "Luxury & Romance", "विलासिता और रोमांस"),
        "Saturn": ("West", "पश्चिम", "Discipline & Stability", "अनुशासन और स्थिरता")
    }
    
    # Find the strongest planet
    strongest_planet = max([p for p in shadbala.keys() if p in DIRECTION_MAP], key=lambda k: shadbala[k])
    d_en, d_hi, b_en, b_hi = DIRECTION_MAP[strongest_planet]
    
    return {
        "planet": strongest_planet,
        "direction_en": d_en,
        "direction_hi": d_hi,
        "benefit_en": f"Your strongest planet is {strongest_planet}. Facing or keeping important items in the {d_en} brings {b_en}.",
        "benefit_hi": f"आपका सबसे मजबूत ग्रह {strongest_planet} है। {d_hi} दिशा की ओर मुख करना या महत्वपूर्ण वस्तुएं रखना {b_hi} लाता है।"
    }
