"""
Jaimini Astrology — Chara Karakas, Arudha Lagna, Karakamsha.

Jaimini is the second great system of Vedic astrology (after Parashara).
It uses variable significators (Chara Karakas) determined by degree,
rather than fixed significators.

Key concepts:
- Chara Karakas: 7 variable significators based on planet's degree in sign
- Arudha Lagna (AL): The "perceived self" / public image
- Upapada Lagna (UL): Marriage/spouse indicator
- Karakamsha: Atmakaraka's Navamsa sign — soul's desire
"""

from __future__ import annotations

from app.core.enums import ZODIAC_SIGNS

SIGN_LORD: dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# The 7 Chara Karakas (ordered from highest to lowest degree)
KARAKA_NAMES = [
    "Atmakaraka",       # Self, soul — highest degree
    "Amatyakaraka",     # Career, minister
    "Bhratrikaraka",    # Siblings, courage
    "Matrikaraka",      # Mother, education
    "Putrakaraka",      # Children, intelligence
    "Gnatikaraka",      # Enemies, diseases, relatives
    "Darakaraka",       # Spouse — lowest degree
]

# Rahu uses (30 - degree) for karaka calculation
KARAKA_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]


def compute_chara_karakas(longitudes: dict[str, float]) -> dict[str, str]:
    """Compute the 7 Chara Karakas based on planetary degrees.

    The planet with the highest degree in its sign becomes Atmakaraka,
    the next becomes Amatyakaraka, etc.

    Rahu's degree is computed as (30 - degree_in_sign) per Jaimini rules.

    Returns: {karaka_name: planet_name}
    """
    degrees: list[tuple[str, float]] = []

    for planet in KARAKA_PLANETS:
        if planet not in longitudes:
            continue
        lon = longitudes[planet]
        deg_in_sign = lon % 30

        if planet == "Rahu":
            # Rahu uses reverse degree
            deg_in_sign = 30.0 - deg_in_sign

        degrees.append((planet, deg_in_sign))

    # Sort by degree descending — highest degree = Atmakaraka
    degrees.sort(key=lambda x: x[1], reverse=True)

    result: dict[str, str] = {}
    for i, (planet, _) in enumerate(degrees):
        if i < len(KARAKA_NAMES):
            result[KARAKA_NAMES[i]] = planet

    return result


def compute_arudha_lagna(
    lagna: str,
    planet_signs: dict[str, str],
) -> str:
    """Compute Arudha Lagna (AL) — the "perceived self" / public image.

    Formula: Find the lord of the 1st house. Count from lagna to that lord's
    sign. Then count the same distance FROM the lord's sign. That sign is AL.

    Example: Aries lagna → Mars rules Aries → Mars in Gemini (3rd from Aries)
    → Count 3 from Gemini → Leo = Arudha Lagna.
    """
    if lagna not in ZODIAC_SIGNS:
        return lagna

    lagna_lord = SIGN_LORD.get(lagna, "")
    if not lagna_lord:
        return lagna

    lord_sign = planet_signs.get(lagna_lord, "")
    if lord_sign not in ZODIAC_SIGNS:
        return lagna

    lagna_idx = ZODIAC_SIGNS.index(lagna)
    lord_idx = ZODIAC_SIGNS.index(lord_sign)

    # Distance from lagna to lord's sign (1-indexed)
    distance = (lord_idx - lagna_idx) % 12

    # Same distance from lord's sign
    al_idx = (lord_idx + distance) % 12
    al_sign = ZODIAC_SIGNS[al_idx]

    # Special rule: if AL falls in lagna (1st) or 7th, move to 10th/4th
    al_house = (al_idx - lagna_idx) % 12 + 1
    if al_house == 1:
        al_idx = (lagna_idx + 9) % 12  # Move to 10th
        al_sign = ZODIAC_SIGNS[al_idx]
    elif al_house == 7:
        al_idx = (lagna_idx + 3) % 12  # Move to 4th
        al_sign = ZODIAC_SIGNS[al_idx]

    return al_sign


def compute_upapada_lagna(
    lagna: str,
    planet_signs: dict[str, str],
) -> str:
    """Compute Upapada Lagna (UL) — spouse/marriage indicator.

    Formula: Arudha of the 12th house.
    Find lord of 12th from lagna. Count distance from 12th sign to lord's sign.
    Apply same distance from lord's sign.
    """
    if lagna not in ZODIAC_SIGNS:
        return lagna

    lagna_idx = ZODIAC_SIGNS.index(lagna)
    twelfth_idx = (lagna_idx + 11) % 12
    twelfth_sign = ZODIAC_SIGNS[twelfth_idx]

    lord_12 = SIGN_LORD.get(twelfth_sign, "")
    if not lord_12:
        return twelfth_sign

    lord_sign = planet_signs.get(lord_12, "")
    if lord_sign not in ZODIAC_SIGNS:
        return twelfth_sign

    lord_idx = ZODIAC_SIGNS.index(lord_sign)
    distance = (lord_idx - twelfth_idx) % 12
    ul_idx = (lord_idx + distance) % 12

    # Special rules: if UL falls in 12th or 6th from lagna, adjust
    ul_house = (ul_idx - lagna_idx) % 12 + 1
    if ul_house == 12:
        ul_idx = (lagna_idx + 8) % 12  # Move to 9th
    elif ul_house == 6:
        ul_idx = (lagna_idx + 2) % 12  # Move to 3rd

    return ZODIAC_SIGNS[ul_idx]


def karakamsha(
    atmakaraka: str,
    longitudes: dict[str, float],
) -> str:
    """Compute Karakamsha — Atmakaraka's Navamsa sign.

    The Navamsa sign of the Atmakaraka indicates the soul's desire
    and the life direction. Its placement is used in Jaimini analysis.
    """
    if atmakaraka not in longitudes:
        return ""

    lon = longitudes[atmakaraka]

    # Compute Navamsa sign (same logic as divisional_charts.py)
    total_navamsa = int(lon / (30.0 / 9))
    navamsa_sign_idx = total_navamsa % 12
    return ZODIAC_SIGNS[navamsa_sign_idx]


def jaimini_karaka_score(
    chara_karakas: dict[str, str],
    natal_planet_signs: dict[str, str],
    natal_planet_houses: dict[str, int],
    lagna: str,
    category: str,
) -> float:
    """Score based on Jaimini karaka placements for a category.

    - Career: Amatyakaraka in kendra/trikona = good
    - Marriage: Darakaraka in 7th, well-placed = good
    - Children: Putrakaraka in 5th, well-placed = good
    - Health: Atmakaraka strong = good
    - Fame: Atmakaraka in 10th or strong AL = good
    - Finance: Amatyakaraka + Atmakaraka in wealth houses = good

    Returns roughly [-0.5, +0.5].
    """
    if not chara_karakas:
        return 0.0

    KENDRA = {1, 4, 7, 10}
    TRIKONA = {1, 5, 9}
    DUSTHANA = {6, 8, 12}

    score = 0.0

    # Category-specific karaka evaluation
    if category in ("career", "fame", "business"):
        ak = chara_karakas.get("Atmakaraka", "")
        amk = chara_karakas.get("Amatyakaraka", "")
        for planet, weight in [(ak, 0.3), (amk, 0.25)]:
            h = natal_planet_houses.get(planet, 0)
            if h in KENDRA:
                score += weight
            elif h in TRIKONA:
                score += weight * 0.8
            elif h in DUSTHANA:
                score -= weight * 0.6

    elif category in ("marriage", "relationships"):
        dk = chara_karakas.get("Darakaraka", "")
        h = natal_planet_houses.get(dk, 0)
        if h == 7:
            score += 0.4  # Ideal: Darakaraka in 7th
        elif h in KENDRA:
            score += 0.2
        elif h in DUSTHANA:
            score -= 0.3

        # Upapada lord strength
        pk = chara_karakas.get("Putrakaraka", "")
        pk_h = natal_planet_houses.get(pk, 0)
        if pk_h in {5, 7, 9}:
            score += 0.1

    elif category == "children":
        pk = chara_karakas.get("Putrakaraka", "")
        h = natal_planet_houses.get(pk, 0)
        if h == 5:
            score += 0.4
        elif h in TRIKONA:
            score += 0.2
        elif h in DUSTHANA:
            score -= 0.3

    elif category == "health":
        ak = chara_karakas.get("Atmakaraka", "")
        h = natal_planet_houses.get(ak, 0)
        if h in KENDRA | TRIKONA:
            score += 0.3
        elif h in DUSTHANA:
            score -= 0.3

    elif category == "education":
        mk = chara_karakas.get("Matrikaraka", "")
        h = natal_planet_houses.get(mk, 0)
        if h in {4, 5, 9}:
            score += 0.3
        elif h in DUSTHANA:
            score -= 0.2

    elif category == "finance":
        ak = chara_karakas.get("Atmakaraka", "")
        amk = chara_karakas.get("Amatyakaraka", "")
        for planet, weight in [(ak, 0.2), (amk, 0.2)]:
            h = natal_planet_houses.get(planet, 0)
            if h in {2, 11}:
                score += weight
            elif h in {1, 5, 9}:
                score += weight * 0.5
            elif h in DUSTHANA:
                score -= weight * 0.5

    else:
        # General: Atmakaraka strength
        ak = chara_karakas.get("Atmakaraka", "")
        h = natal_planet_houses.get(ak, 0)
        if h in KENDRA | TRIKONA:
            score += 0.2
        elif h in DUSTHANA:
            score -= 0.2

    return round(score, 3)


def arudha_lagna_score(
    arudha_sign: str,
    lagna: str,
    category: str,
) -> float:
    """Score the Arudha Lagna placement for a category.

    AL in strong houses from lagna = good public image/perception.
    AL in weak houses = challenges in public life.

    Returns roughly [-0.3, +0.3].
    """
    if arudha_sign not in ZODIAC_SIGNS or lagna not in ZODIAC_SIGNS:
        return 0.0

    lagna_idx = ZODIAC_SIGNS.index(lagna)
    al_idx = ZODIAC_SIGNS.index(arudha_sign)
    al_house = (al_idx - lagna_idx) % 12 + 1

    # AL in 1st, 2nd, 4th, 5th, 7th, 9th, 10th, 11th are generally good
    good_al = {1, 2, 4, 5, 7, 9, 10, 11}
    bad_al = {6, 8, 12}

    if category in ("fame", "career", "business"):
        # AL matters most for public-facing categories
        if al_house in {10, 11, 1}:
            return 0.3
        elif al_house in good_al:
            return 0.15
        elif al_house in bad_al:
            return -0.25
    elif category in ("marriage", "relationships"):
        if al_house == 7:
            return 0.2
        elif al_house in good_al:
            return 0.1
        elif al_house in bad_al:
            return -0.15
    else:
        if al_house in good_al:
            return 0.1
        elif al_house in bad_al:
            return -0.1

    return 0.0
