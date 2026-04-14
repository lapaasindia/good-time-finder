"""
Simplified Shadbala (Six-fold Planetary Strength).

Full Shadbala is extremely complex. This implements a practical
subset that captures the most significant strength indicators.

Returns a normalized strength score (0.0–2.0) per planet.
"""

from __future__ import annotations

import swisseph as swe

from app.core.enums import ZODIAC_SIGNS

EXALTATION_SIGN: dict[str, str] = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
}

DEBILITATION_SIGN: dict[str, str] = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
}

OWN_SIGNS: dict[str, list[str]] = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
}

FRIENDLY_PLANETS: dict[str, set[str]] = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}

ENEMY_PLANETS: dict[str, set[str]] = {
    "Sun": {"Venus", "Saturn"},
    "Moon": {"Rahu", "Ketu"},
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
}

NAISARGIKA_STRENGTH: dict[str, float] = {
    "Saturn": 0.17,
    "Mars": 0.33,
    "Mercury": 0.50,
    "Jupiter": 0.67,
    "Venus": 0.83,
    "Moon": 0.50,
    "Sun": 1.00,
}

DIG_BALA_BEST_HOUSE: dict[str, int] = {
    "Sun": 10,
    "Mars": 10,
    "Jupiter": 1,
    "Mercury": 1,
    "Moon": 4,
    "Venus": 4,
    "Saturn": 7,
}


def _sthanabala(planet: str, sign: str) -> float:
    if sign == EXALTATION_SIGN.get(planet):
        return 1.0
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return 0.75
    if sign == DEBILITATION_SIGN.get(planet):
        return 0.0
    return 0.35


def _digbala(planet: str, house: int) -> float:
    best = DIG_BALA_BEST_HOUSE.get(planet, 1)
    distance = abs(house - best)
    if distance > 6:
        distance = 12 - distance
    return max(0.0, 1.0 - distance / 6.0)


def _naisargika(planet: str) -> float:
    return NAISARGIKA_STRENGTH.get(planet, 0.3)


def planet_strength(
    planet: str,
    sign: str,
    house: int,
) -> float:
    sthan = _sthanabala(planet, sign)
    dig = _digbala(planet, house)
    nais = _naisargika(planet)
    raw = (sthan * 0.4 + dig * 0.3 + nais * 0.3)
    return round(raw * 2.0, 3)


def shadbala_summary(
    planet_signs: dict[str, str],
    planet_houses: dict[str, int],
) -> dict[str, float]:
    result: dict[str, float] = {}
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for p in planets:
        sign = planet_signs.get(p, "")
        house = planet_houses.get(p, 1)
        if sign:
            result[p] = planet_strength(p, sign, house)
    return result


def benefic_strength_score(
    shadbala: dict[str, float],
    relevant_planets: set[str],
) -> float:
    if not relevant_planets:
        return 0.0
    scores = [shadbala.get(p, 0.0) for p in relevant_planets]
    return round(sum(scores) / len(scores), 3)
