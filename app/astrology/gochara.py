"""
Gochara (Transit) scoring.

Evaluates current planetary transits relative to the natal Moon sign.
Classical Vedic gochara tables define which houses from natal Moon
are good/bad for each transiting planet.
"""

from __future__ import annotations

from app.core.enums import ZODIAC_SIGNS
from app.astrology.shadbala import EXALTATION_SIGN, DEBILITATION_SIGN, OWN_SIGNS

GOOD_HOUSES_FROM_NATAL_MOON: dict[str, set[int]] = {
    "Sun":     {3, 6, 10, 11},
    "Moon":    {1, 3, 6, 7, 10, 11},
    "Mars":    {3, 6, 11},
    "Mercury": {2, 4, 6, 8, 10, 11},
    "Jupiter": {2, 5, 7, 9, 11},
    "Venus":   {1, 2, 3, 4, 5, 8, 9, 11, 12},
    "Saturn":  {3, 6, 11},
    "Rahu":    {3, 6, 11},
    "Ketu":    {3, 6, 11},
}

BAD_HOUSES_FROM_NATAL_MOON: dict[str, set[int]] = {
    "Sun":     {1, 2, 4, 5, 7, 8, 9, 12},
    "Moon":    {4, 8, 12},
    "Mars":    {1, 2, 4, 5, 7, 8, 9, 12},
    "Mercury": {1, 3, 5, 7, 9, 12},
    "Jupiter": {1, 3, 4, 6, 8, 10, 12},
    "Venus":   {6, 7, 10},
    "Saturn":  {1, 2, 4, 5, 7, 8, 9, 12},
    "Rahu":    {1, 2, 4, 5, 7, 8, 9, 12},
    "Ketu":    {1, 2, 4, 5, 7, 8, 9, 12},
}

PLANET_GOCHARA_WEIGHT: dict[str, float] = {
    "Jupiter": 2.0,
    "Saturn":  1.8,
    "Rahu":    1.5,
    "Ketu":    1.5,
    "Mars":    1.2,
    "Sun":     1.0,
    "Moon":    1.0,
    "Mercury": 0.8,
    "Venus":   0.8,
}


def _house_from_sign(transit_sign: str, natal_sign: str) -> int:
    moon_index = ZODIAC_SIGNS.index(natal_sign)
    transit_index = ZODIAC_SIGNS.index(transit_sign)
    return ((transit_index - moon_index) % 12) + 1


def gochara_score(
    planet_signs: dict[str, str],
    natal_moon_sign: str,
    natal_lagna: str | None = None,
) -> dict[str, float]:
    scores: dict[str, float] = {}
    for planet, transit_sign in planet_signs.items():
        if transit_sign not in ZODIAC_SIGNS:
            scores[planet] = 0.0
            continue
        
        weight = PLANET_GOCHARA_WEIGHT.get(planet, 1.0)
        good = GOOD_HOUSES_FROM_NATAL_MOON.get(planet, set())
        bad = BAD_HOUSES_FROM_NATAL_MOON.get(planet, set())

        # Score from Moon (standard)
        house_moon = _house_from_sign(transit_sign, natal_moon_sign)
        s_moon = 0.0
        if house_moon in good:
            s_moon = weight
        elif house_moon in bad:
            s_moon = -weight

        # Score from Lagna (if available) - secondary but important for physical/career
        s_lagna = 0.0
        if natal_lagna:
            house_lagna = _house_from_sign(transit_sign, natal_lagna)
            # Lagna transit is supplementary (weight 0.35) to avoid double-counting with Moon
            if house_lagna in good:
                s_lagna = weight * 0.35
            elif house_lagna in bad:
                s_lagna = -weight * 0.35
        
        # Transit dignity modifier: planet in own/exalted sign is inherently strong
        # Strong transits have reduced negative effects and amplified positive effects
        raw = s_moon + s_lagna
        if transit_sign == EXALTATION_SIGN.get(planet, ""):
            # Exalted planet: negative effects reduced by 40%, positive boosted by 20%
            if raw < 0:
                raw *= 0.6
            else:
                raw *= 1.2
        elif transit_sign in OWN_SIGNS.get(planet, []):
            # Own sign: negative effects reduced by 30%, positive boosted by 15%
            if raw < 0:
                raw *= 0.7
            else:
                raw *= 1.15
        elif transit_sign == DEBILITATION_SIGN.get(planet, ""):
            # Debilitated planet: negative effects amplified by 25%
            if raw < 0:
                raw *= 1.25

        scores[planet] = round(raw, 3)

    return scores


def total_gochara_score(
    planet_signs: dict[str, str],
    natal_moon_sign: str,
    natal_lagna: str | None = None,
) -> float:
    scores = gochara_score(planet_signs, natal_moon_sign, natal_lagna)
    return round(sum(scores.values()), 3)


def transit_over_natal_bonus(
    transit_signs: dict[str, str],
    natal_signs: dict[str, str],
    relevant_planets: set[str],
) -> float:
    """Bonus/penalty when slow planets transit over KEY natal planet positions.
    
    Jupiter over natal Sun/Moon = blessing (+)
    Saturn over natal Sun/Moon = affliction (-)
    Only check Sun and Moon to avoid over-triggering (malefics are always somewhere).
    """
    bonus = 0.0
    key_natal = {"Sun", "Moon"}
    
    for natal_p in key_natal:
        natal_s = natal_signs.get(natal_p)
        if not natal_s:
            continue
        
        # Jupiter transiting over natal Sun/Moon
        jup_transit = transit_signs.get("Jupiter", "")
        if jup_transit == natal_s:
            bonus += 0.5
        
        # Saturn transiting over natal Sun/Moon (Sade Sati-like for Sun)
        sat_transit = transit_signs.get("Saturn", "")
        if sat_transit == natal_s:
            bonus -= 0.4
        
        # Rahu over natal Sun/Moon (eclipse-like effect)
        rahu_transit = transit_signs.get("Rahu", "")
        if rahu_transit == natal_s:
            bonus -= 0.3
    
    return round(bonus, 3)


def category_gochara_score(
    planet_signs: dict[str, str],
    natal_moon_sign: str,
    relevant_planets: set[str],
    natal_lagna: str | None = None,
    natal_planet_signs: dict[str, str] | None = None,
) -> float:
    scores = gochara_score(planet_signs, natal_moon_sign, natal_lagna)
    if not scores:
        return 0.0
    relevant_sum = sum(s for p, s in scores.items() if p in relevant_planets)
    background_sum = sum(s * 0.3 for p, s in scores.items() if p not in relevant_planets)
    
    return round(relevant_sum + background_sum, 3)
