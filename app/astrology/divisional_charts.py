"""
Divisional Charts (Varga) — D2, D3, D7, D9, D10.

D2  (Hora):     Wealth and financial strength.
D3  (Drekkana): Siblings, courage, initiative.
D7  (Saptamsa): Children and progeny.
D9  (Navamsa):  Marriage, dharma, spiritual potential. Most important varga.
D10 (Dasamsa):  Career and professional life.

Calculation:
  - For each planet, take its sidereal longitude.
  - D9: Navamsa sign = (sign_index * 9 + pada_in_sign) mapped to zodiac
  - D10: Dasamsa sign = (sign_index * 10 + dasamsa_portion) mapped to zodiac
"""

from __future__ import annotations

from app.core.enums import ZODIAC_SIGNS
from app.astrology.shadbala import EXALTATION_SIGN, DEBILITATION_SIGN, OWN_SIGNS


def _longitude_to_d9_sign(longitude: float) -> str:
    """Map a sidereal longitude to its Navamsa (D9) sign.

    Each sign (30°) is divided into 9 Navamsas of 3°20' each.
    The starting Navamsa depends on the element of the sign:
      - Fire signs (Aries, Leo, Sag) start from Aries
      - Earth signs (Tau, Vir, Cap) start from Capricorn
      - Air signs (Gem, Lib, Aqu) start from Libra
      - Water signs (Can, Sco, Pis) start from Cancer
    """
    sign_index = int(longitude / 30) % 12
    degree_in_sign = longitude % 30
    navamsa_in_sign = int(degree_in_sign / (30.0 / 9))  # 0–8

    # Starting navamsa offset per sign element
    fire_signs = {0, 4, 8}    # Aries, Leo, Sagittarius
    earth_signs = {1, 5, 9}   # Taurus, Virgo, Capricorn
    air_signs = {2, 6, 10}    # Gemini, Libra, Aquarius
    # water_signs = {3, 7, 11}  # Cancer, Scorpio, Pisces

    if sign_index in fire_signs:
        start = 0   # Aries
    elif sign_index in earth_signs:
        start = 9   # Capricorn
    elif sign_index in air_signs:
        start = 6   # Libra
    else:
        start = 3   # Cancer

    d9_index = (start + navamsa_in_sign) % 12
    return ZODIAC_SIGNS[d9_index]


def _longitude_to_d10_sign(longitude: float) -> str:
    """Map a sidereal longitude to its Dasamsa (D10) sign.

    Each sign (30°) is divided into 10 Dasamsas of 3° each.
    For odd signs, counting starts from the sign itself.
    For even signs, counting starts from the 9th sign from it.
    """
    sign_index = int(longitude / 30) % 12
    degree_in_sign = longitude % 30
    dasamsa_in_sign = int(degree_in_sign / 3.0)  # 0–9
    if dasamsa_in_sign > 9:
        dasamsa_in_sign = 9

    # Odd signs (1-indexed: 1,3,5...) start from themselves
    # Even signs (2,4,6...) start from 9th sign from them
    if sign_index % 2 == 0:  # Odd sign (0-indexed even = 1-indexed odd)
        start = sign_index
    else:
        start = (sign_index + 8) % 12  # 9th from sign

    d10_index = (start + dasamsa_in_sign) % 12
    return ZODIAC_SIGNS[d10_index]


def compute_d9_positions(longitudes: dict[str, float]) -> dict[str, str]:
    """Compute Navamsa (D9) sign for each planet given sidereal longitudes."""
    return {planet: _longitude_to_d9_sign(lon)
            for planet, lon in longitudes.items()}


def compute_d10_positions(longitudes: dict[str, float]) -> dict[str, str]:
    """Compute Dasamsa (D10) sign for each planet given sidereal longitudes."""
    return {planet: _longitude_to_d10_sign(lon)
            for planet, lon in longitudes.items()}


def is_vargottama(d1_sign: str, d9_sign: str) -> bool:
    """Planet in same sign in D1 (rashi) and D9 (navamsa) = Vargottama.
    Vargottama planets are exceptionally strong — like being exalted."""
    return d1_sign == d9_sign


def d9_strength_score(
    planet: str,
    d9_sign: str,
    d1_sign: str,
) -> float:
    """Score a planet's D9 (Navamsa) placement.

    Returns roughly [-0.5, +0.8]:
      - Vargottama: +0.5 bonus
      - Exalted in D9: +0.3
      - Own sign in D9: +0.2
      - Debilitated in D9: -0.3
    """
    score = 0.0

    if is_vargottama(d1_sign, d9_sign):
        score += 0.5

    if d9_sign == EXALTATION_SIGN.get(planet, ""):
        score += 0.3
    elif d9_sign in OWN_SIGNS.get(planet, []):
        score += 0.2
    elif d9_sign == DEBILITATION_SIGN.get(planet, ""):
        score -= 0.3

    return round(score, 3)


def d10_strength_score(
    planet: str,
    d10_sign: str,
    d1_sign: str,
) -> float:
    """Score a planet's D10 (Dasamsa) placement for career.

    Returns roughly [-0.4, +0.7]:
      - Vargottama (D1==D10): +0.4 bonus
      - Exalted in D10: +0.3
      - Own sign in D10: +0.2
      - Debilitated in D10: -0.3
    """
    score = 0.0

    # Vargottama in D10 (same sign in rashi and dasamsa)
    if d1_sign == d10_sign:
        score += 0.4

    if d10_sign == EXALTATION_SIGN.get(planet, ""):
        score += 0.3
    elif d10_sign in OWN_SIGNS.get(planet, []):
        score += 0.2
    elif d10_sign == DEBILITATION_SIGN.get(planet, ""):
        score -= 0.3

    return round(score, 3)


def navamsa_score_for_category(
    longitudes: dict[str, float],
    planet_signs_d1: dict[str, str],
    category: str,
    relevant_planets: set[str],
) -> float:
    """Aggregate D9 navamsa strength for category-relevant planets.

    For marriage/relationships: all D9 scores matter heavily.
    For other categories: only relevant planet D9 scores contribute.
    """
    d9_signs = compute_d9_positions(longitudes)

    total = 0.0
    count = 0
    for planet in relevant_planets:
        if planet not in d9_signs or planet not in planet_signs_d1:
            continue
        s = d9_strength_score(planet, d9_signs[planet], planet_signs_d1[planet])
        total += s
        count += 1

    # For marriage/relationships, also check Venus and 7th lord in D9
    if category in ("marriage", "relationships"):
        for extra in ("Venus", "Jupiter", "Moon"):
            if extra not in relevant_planets and extra in d9_signs and extra in planet_signs_d1:
                s = d9_strength_score(extra, d9_signs[extra], planet_signs_d1[extra])
                total += s * 0.5  # supplementary weight
                count += 1

    return round(total, 3)


def dasamsa_score_for_category(
    longitudes: dict[str, float],
    planet_signs_d1: dict[str, str],
    category: str,
    relevant_planets: set[str],
) -> float:
    """Aggregate D10 dasamsa strength for career-related categories.

    Only applies to career, fame, business, legal categories.
    For other categories, returns 0.
    """
    if category not in ("career", "fame", "business", "legal", "finance"):
        return 0.0

    d10_signs = compute_d10_positions(longitudes)

    total = 0.0
    for planet in relevant_planets:
        if planet not in d10_signs or planet not in planet_signs_d1:
            continue
        total += d10_strength_score(planet, d10_signs[planet], planet_signs_d1[planet])

    # Sun and Saturn are always important for career in D10
    for extra in ("Sun", "Saturn"):
        if extra not in relevant_planets and extra in d10_signs and extra in planet_signs_d1:
            total += d10_strength_score(extra, d10_signs[extra], planet_signs_d1[extra]) * 0.5

    return round(total, 3)


# ═══════════════════════════════════════════════════════════════════
# D2 — Hora (Wealth Chart)
# ═══════════════════════════════════════════════════════════════════
# Each sign is divided into 2 Horas of 15° each.
# In odd signs: first 15° = Sun Hora (Leo), second 15° = Moon Hora (Cancer)
# In even signs: first 15° = Moon Hora (Cancer), second 15° = Sun Hora (Leo)

def _longitude_to_d2_sign(longitude: float) -> str:
    """Map a sidereal longitude to its Hora (D2) sign."""
    sign_index = int(longitude / 30) % 12
    degree_in_sign = longitude % 30
    first_half = degree_in_sign < 15.0

    if sign_index % 2 == 0:  # Odd signs (0-indexed even)
        return "Leo" if first_half else "Cancer"
    else:  # Even signs
        return "Cancer" if first_half else "Leo"


def compute_d2_positions(longitudes: dict[str, float]) -> dict[str, str]:
    """Compute Hora (D2) sign for each planet."""
    return {planet: _longitude_to_d2_sign(lon)
            for planet, lon in longitudes.items()}


def d2_strength_score(planet: str, d2_sign: str) -> float:
    """Score a planet's D2 Hora placement for wealth.

    Sun and Mars in Sun Hora (Leo) = strong for self-earned wealth.
    Moon, Venus in Moon Hora (Cancer) = strong for property/inherited wealth.
    Jupiter is strong in either Hora.

    Returns roughly [-0.2, +0.3].
    """
    sun_hora_planets = {"Sun", "Mars", "Saturn"}
    moon_hora_planets = {"Moon", "Venus", "Mercury"}

    if d2_sign == "Leo":  # Sun Hora
        if planet in sun_hora_planets:
            return 0.25
        elif planet == "Jupiter":
            return 0.2
        elif planet in moon_hora_planets:
            return 0.0
        else:
            return 0.05
    elif d2_sign == "Cancer":  # Moon Hora
        if planet in moon_hora_planets:
            return 0.25
        elif planet == "Jupiter":
            return 0.2
        elif planet in sun_hora_planets:
            return 0.0
        else:
            return 0.05

    return 0.0


def hora_score_for_category(
    longitudes: dict[str, float],
    category: str,
    relevant_planets: set[str],
) -> float:
    """Aggregate D2 Hora strength — only for finance/property categories."""
    if category not in ("finance", "property", "business"):
        return 0.0

    d2_signs = compute_d2_positions(longitudes)
    total = 0.0
    for planet in relevant_planets:
        if planet in d2_signs:
            total += d2_strength_score(planet, d2_signs[planet])

    # Always check Jupiter (wealth karaka)
    if "Jupiter" not in relevant_planets and "Jupiter" in d2_signs:
        total += d2_strength_score("Jupiter", d2_signs["Jupiter"]) * 0.5

    return round(total, 3)


# ═══════════════════════════════════════════════════════════════════
# D3 — Drekkana (Siblings/Courage Chart)
# ═══════════════════════════════════════════════════════════════════
# Each sign is divided into 3 Drekkanas of 10° each.
# 1st Drekkana (0-10°): same sign
# 2nd Drekkana (10-20°): 5th sign from it
# 3rd Drekkana (20-30°): 9th sign from it

def _longitude_to_d3_sign(longitude: float) -> str:
    """Map a sidereal longitude to its Drekkana (D3) sign."""
    sign_index = int(longitude / 30) % 12
    degree_in_sign = longitude % 30

    if degree_in_sign < 10.0:
        d3_index = sign_index  # Same sign
    elif degree_in_sign < 20.0:
        d3_index = (sign_index + 4) % 12  # 5th from sign
    else:
        d3_index = (sign_index + 8) % 12  # 9th from sign

    return ZODIAC_SIGNS[d3_index]


def compute_d3_positions(longitudes: dict[str, float]) -> dict[str, str]:
    """Compute Drekkana (D3) sign for each planet."""
    return {planet: _longitude_to_d3_sign(lon)
            for planet, lon in longitudes.items()}


def d3_strength_score(planet: str, d3_sign: str, d1_sign: str) -> float:
    """Score a planet's D3 placement.

    Same logic as D9 — exaltation/own/debilitation in D3,
    plus Vargottama bonus (same sign in D1 and D3).
    Returns roughly [-0.3, +0.5].
    """
    score = 0.0
    if d1_sign == d3_sign:
        score += 0.3  # Vargottama in D3
    if d3_sign == EXALTATION_SIGN.get(planet, ""):
        score += 0.2
    elif d3_sign in OWN_SIGNS.get(planet, []):
        score += 0.15
    elif d3_sign == DEBILITATION_SIGN.get(planet, ""):
        score -= 0.2
    return round(score, 3)


# ═══════════════════════════════════════════════════════════════════
# D7 — Saptamsa (Children Chart)
# ═══════════════════════════════════════════════════════════════════
# Each sign is divided into 7 Saptamsas of 4°17'8.6" each.
# In odd signs: starts from same sign and counts forward
# In even signs: starts from 7th sign and counts forward

def _longitude_to_d7_sign(longitude: float) -> str:
    """Map a sidereal longitude to its Saptamsa (D7) sign."""
    sign_index = int(longitude / 30) % 12
    degree_in_sign = longitude % 30
    saptamsa_in_sign = int(degree_in_sign / (30.0 / 7))  # 0–6
    if saptamsa_in_sign > 6:
        saptamsa_in_sign = 6

    if sign_index % 2 == 0:  # Odd sign
        start = sign_index
    else:  # Even sign
        start = (sign_index + 6) % 12  # 7th from sign

    d7_index = (start + saptamsa_in_sign) % 12
    return ZODIAC_SIGNS[d7_index]


def compute_d7_positions(longitudes: dict[str, float]) -> dict[str, str]:
    """Compute Saptamsa (D7) sign for each planet."""
    return {planet: _longitude_to_d7_sign(lon)
            for planet, lon in longitudes.items()}


def d7_strength_score(planet: str, d7_sign: str, d1_sign: str) -> float:
    """Score a planet's D7 placement for children/progeny.

    Returns roughly [-0.3, +0.5].
    """
    score = 0.0
    if d1_sign == d7_sign:
        score += 0.3  # Vargottama in D7
    if d7_sign == EXALTATION_SIGN.get(planet, ""):
        score += 0.2
    elif d7_sign in OWN_SIGNS.get(planet, []):
        score += 0.15
    elif d7_sign == DEBILITATION_SIGN.get(planet, ""):
        score -= 0.2
    return round(score, 3)


def saptamsa_score_for_category(
    longitudes: dict[str, float],
    planet_signs_d1: dict[str, str],
    category: str,
    relevant_planets: set[str],
) -> float:
    """Aggregate D7 Saptamsa strength — mainly for children category."""
    if category != "children":
        return 0.0

    d7_signs = compute_d7_positions(longitudes)
    total = 0.0
    for planet in relevant_planets:
        if planet in d7_signs and planet in planet_signs_d1:
            total += d7_strength_score(planet, d7_signs[planet], planet_signs_d1[planet])

    # Jupiter (putra karaka) always checked
    if "Jupiter" not in relevant_planets and "Jupiter" in d7_signs and "Jupiter" in planet_signs_d1:
        total += d7_strength_score("Jupiter", d7_signs["Jupiter"], planet_signs_d1["Jupiter"]) * 0.5

    return round(total, 3)


# ═══════════════════════════════════════════════════════════════════
# Vimsopaka Bala — 20-point multi-varga strength
# ═══════════════════════════════════════════════════════════════════
# Simplified version using D1, D2, D3, D7, D9, D10.

def vimsopaka_score(
    planet: str,
    d1_sign: str,
    longitudes: dict[str, float],
) -> float:
    """Simplified Vimsopaka Bala using available divisional charts.

    Evaluates planet's dignity across D1, D2, D3, D7, D9, D10.
    Returns roughly [-1.0, +2.0] — aggregate multi-varga strength.
    """
    if planet not in longitudes:
        return 0.0

    lon = longitudes[planet]
    score = 0.0

    # D1 contribution (weight 3.5/20)
    if d1_sign == EXALTATION_SIGN.get(planet, ""):
        score += 0.35
    elif d1_sign in OWN_SIGNS.get(planet, []):
        score += 0.25
    elif d1_sign == DEBILITATION_SIGN.get(planet, ""):
        score -= 0.35

    # D9 contribution (weight 3.0/20)
    d9_sign = _longitude_to_d9_sign(lon)
    if d9_sign == EXALTATION_SIGN.get(planet, ""):
        score += 0.30
    elif d9_sign in OWN_SIGNS.get(planet, []):
        score += 0.20
    elif d9_sign == DEBILITATION_SIGN.get(planet, ""):
        score -= 0.30

    # D2 contribution (weight 1.5/20)
    d2_sign = _longitude_to_d2_sign(lon)
    if planet in ("Sun", "Mars") and d2_sign == "Leo":
        score += 0.15
    elif planet in ("Moon", "Venus") and d2_sign == "Cancer":
        score += 0.15

    # D3 contribution (weight 1.5/20)
    d3_sign = _longitude_to_d3_sign(lon)
    if d3_sign == EXALTATION_SIGN.get(planet, ""):
        score += 0.15
    elif d3_sign in OWN_SIGNS.get(planet, []):
        score += 0.10
    elif d3_sign == DEBILITATION_SIGN.get(planet, ""):
        score -= 0.15

    # D7 contribution (weight 1.0/20)
    d7_sign = _longitude_to_d7_sign(lon)
    if d7_sign == EXALTATION_SIGN.get(planet, ""):
        score += 0.10
    elif d7_sign in OWN_SIGNS.get(planet, []):
        score += 0.08
    elif d7_sign == DEBILITATION_SIGN.get(planet, ""):
        score -= 0.10

    # D10 contribution (weight 1.5/20)
    d10_sign = _longitude_to_d10_sign(lon)
    if d10_sign == EXALTATION_SIGN.get(planet, ""):
        score += 0.15
    elif d10_sign in OWN_SIGNS.get(planet, []):
        score += 0.10
    elif d10_sign == DEBILITATION_SIGN.get(planet, ""):
        score -= 0.15

    return round(score, 3)


def vimsopaka_for_category(
    longitudes: dict[str, float],
    planet_signs_d1: dict[str, str],
    relevant_planets: set[str],
) -> float:
    """Aggregate Vimsopaka score across relevant planets."""
    total = 0.0
    count = 0
    for planet in relevant_planets:
        d1_sign = planet_signs_d1.get(planet, "")
        if d1_sign and planet in longitudes:
            total += vimsopaka_score(planet, d1_sign, longitudes)
            count += 1
    if count == 0:
        return 0.0
    return round(total / count, 3)
