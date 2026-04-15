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


# ── Cheshta Bala (Motional Strength) ──
# Retrograde planets gain cheshta bala. Stationary planets have maximum.
# Sun and Moon are never retrograde, so they get average cheshta.
def _cheshtabala(planet: str, speed: float | None = None) -> float:
    """Cheshta Bala based on planetary motion.

    Retrograde → high cheshta (planet is closer to Earth)
    Stationary → maximum cheshta
    Normal direct → moderate cheshta
    """
    if planet in ("Sun", "Moon"):
        return 0.5  # Always direct, average cheshta

    if speed is None:
        return 0.5  # Default if speed not available

    if abs(speed) < 0.01:
        return 1.0  # Stationary — maximum
    elif speed < 0:
        return 0.8  # Retrograde — strong cheshta
    else:
        return 0.4  # Normal direct


# ── Kala Bala (Temporal Strength) ──
# Planets are strong during certain times:
# - Diurnal planets (Sun, Jupiter, Venus) strong during day
# - Nocturnal planets (Moon, Mars, Saturn) strong during night
# - Mercury is strong always (amphibious)
DIURNAL_PLANETS = {"Sun", "Jupiter", "Venus"}
NOCTURNAL_PLANETS = {"Moon", "Mars", "Saturn"}


def _kalabala(planet: str, is_daytime: bool = True) -> float:
    """Kala Bala based on whether it's day or night."""
    if planet == "Mercury":
        return 0.6  # Always moderate
    if planet in DIURNAL_PLANETS:
        return 0.8 if is_daytime else 0.3
    if planet in NOCTURNAL_PLANETS:
        return 0.3 if is_daytime else 0.8
    return 0.5


# ── Drik Bala (Aspectual Strength) ──
# Planets aspected by benefics gain strength.
# Planets aspected by malefics lose strength.
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Saturn", "Mars", "Sun", "Rahu", "Ketu"}


def _drikbala(
    planet: str,
    planet_houses: dict[str, int],
) -> float:
    """Drik Bala — strength from aspects received.

    Checks which planets aspect (7th house = standard aspect) this planet.
    Benefic aspects add strength, malefic aspects reduce it.
    """
    target_house = planet_houses.get(planet, 0)
    if not target_house:
        return 0.0

    score = 0.0
    for other_planet, other_house in planet_houses.items():
        if other_planet == planet:
            continue
        # Standard 7th house aspect (all planets)
        aspect_house = ((other_house + 6) % 12) + 1
        # Handle the 12→1 wrap
        if other_house == 6:
            aspect_house = 12
        elif other_house == 7:
            aspect_house = 1
        else:
            diff = target_house - other_house
            if diff < 0:
                diff += 12
            if diff == 6:  # 7th house aspect
                if other_planet in NATURAL_BENEFICS:
                    score += 0.15
                elif other_planet in NATURAL_MALEFICS:
                    score -= 0.15

        # Special aspects
        if other_planet == "Jupiter":
            # Jupiter's 5th and 9th aspects
            for asp_offset in [4, 8]:
                if (other_house + asp_offset - 1) % 12 + 1 == target_house:
                    score += 0.1
        elif other_planet == "Mars":
            # Mars's 4th and 8th aspects
            for asp_offset in [3, 7]:
                if (other_house + asp_offset - 1) % 12 + 1 == target_house:
                    score -= 0.1
        elif other_planet == "Saturn":
            # Saturn's 3rd and 10th aspects
            for asp_offset in [2, 9]:
                if (other_house + asp_offset - 1) % 12 + 1 == target_house:
                    score -= 0.1

    return max(-0.5, min(0.5, score))


def planet_strength(
    planet: str,
    sign: str,
    house: int,
    speed: float | None = None,
    is_daytime: bool = True,
    planet_houses: dict[str, int] | None = None,
) -> float:
    """Full Shadbala — all six components.

    1. Sthana Bala (positional) — sign placement
    2. Dig Bala (directional) — house placement
    3. Naisargika Bala (natural) — inherent strength
    4. Cheshta Bala (motional) — speed/retrograde
    5. Kala Bala (temporal) — day/night
    6. Drik Bala (aspectual) — aspects received
    """
    sthan = _sthanabala(planet, sign)
    dig = _digbala(planet, house)
    nais = _naisargika(planet)
    cheshta = _cheshtabala(planet, speed)
    kala = _kalabala(planet, is_daytime)
    drik = _drikbala(planet, planet_houses) if planet_houses else 0.0

    # Weighted combination of all 6 components
    raw = (
        sthan * 0.25 +
        dig * 0.20 +
        nais * 0.15 +
        cheshta * 0.15 +
        kala * 0.10 +
        drik * 0.15
    )
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
            result[p] = planet_strength(p, sign, house, planet_houses=planet_houses)
    return result


SIGN_LORD: dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}


def lagna_lord_strength(
    lagna: str,
    shadbala: dict[str, float],
    natal_houses: dict[str, int],
) -> float:
    """Score based on lagna lord's strength and house placement.

    The lord of the ascendant is the most important planet in a chart.
    Its strength and placement directly modify all life outcomes.

    Returns a value in roughly [-1.0, +1.0]:
      - Strong lagna lord in kendra/trikona: positive boost
      - Weak lagna lord in dusthana: negative drag
      - Average placement: near zero
    """
    lord = SIGN_LORD.get(lagna)
    if not lord:
        return 0.0

    strength = shadbala.get(lord, 1.0)  # 0.0–2.0 range
    house = natal_houses.get(lord, 1)

    # Placement score: kendra/trikona = positive, dusthana = negative
    if house in {1, 4, 7, 10}:     # Kendra
        placement = 0.4
    elif house in {5, 9}:           # Trikona
        placement = 0.5
    elif house in {6, 8, 12}:       # Dusthana
        placement = -0.4
    elif house in {2, 11}:          # Wealth/Gains
        placement = 0.2
    else:                           # 3rd house
        placement = 0.0

    # Combine: strength centered around 1.0, so (strength - 1.0) is in [-1, +1]
    strength_factor = (strength - 1.0) * 0.5  # [-0.5, +0.5]

    return round(strength_factor + placement, 3)


def benefic_strength_score(
    shadbala: dict[str, float],
    relevant_planets: set[str],
) -> float:
    if not relevant_planets:
        return 0.0
    scores = [shadbala.get(p, 0.0) for p in relevant_planets]
    return round(sum(scores) / len(scores), 3)
