"""
Planetary Avasthas — States/Ages of Planets.

Per Brihat Parashara Hora Shastra (BPHS), planets exist in 5 age states
based on their degree position within their sign. This affects how
effectively they deliver their results.

Also includes:
- Pushkara Navamsa/Bhaga detection (highly auspicious degrees)
- Transit speed weighting (stationary planets have maximum effect)
"""

from __future__ import annotations

from app.core.enums import ZODIAC_SIGNS

# ── Planetary Age States (Baaladi Avasthas) ──
# Degree ranges depend on whether the sign is odd or even.
# Odd signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius):
#   0-6° = Bala (infant), 6-12° = Kumara (youth), 12-18° = Yuva (adult),
#   18-24° = Vriddha (old), 24-30° = Mrita (dead)
# Even signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces):
#   Reversed: 0-6° = Mrita, 6-12° = Vriddha, 12-18° = Yuva,
#   18-24° = Kumara, 24-30° = Bala

from dataclasses import dataclass

@dataclass
class PlanetAvastha:
    planet: str
    state_en: str
    state_hi: str
    score: float

ODD_SIGN_INDICES = {0, 2, 4, 6, 8, 10}  # Aries, Gemini, Leo, Libra, Sag, Aquarius
EVEN_SIGN_INDICES = {1, 3, 5, 7, 9, 11}  # Taurus, Cancer, Virgo, Scorpio, Cap, Pisces

AVASTHA_NAMES = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]

AVASTHA_STRENGTH: dict[str, float] = {
    "Bala":    0.25,   # Infant — planet is weak, immature results
    "Kumara":  0.50,   # Youth — growing, moderate results
    "Yuva":    1.00,   # Adult — full strength, complete results
    "Vriddha": 0.50,   # Old — declining, partial results
    "Mrita":   0.10,   # Dead — almost no ability to deliver
}


def compute_all_avasthas(longitudes: dict[str, float]) -> dict[str, PlanetAvastha]:
    """Calculate the Avasthas for all given planets in both Hindi and English."""
    result = {}
    hi_map = {
        "Bala": "बाल",
        "Kumara": "कुमार",
        "Yuva": "युवा",
        "Vriddha": "वृद्ध",
        "Mrita": "मृत"
    }
    
    for planet, lon in longitudes.items():
        if planet in {"Lagna", "Uranus", "Neptune", "Pluto"}:
            continue
        state_en, score = compute_avastha(lon)
        state_hi = hi_map.get(state_en, state_en)
        result[planet] = PlanetAvastha(planet, state_en, state_hi, score)
        
    return result

def compute_avastha(longitude: float) -> tuple[str, float]:
    """Determine planetary avastha (age state) from sidereal longitude.

    Returns (avastha_name, strength_multiplier).
    """
    sign_index = int(longitude / 30) % 12
    degree_in_sign = longitude % 30

    if sign_index in ODD_SIGN_INDICES:
        # Normal order for odd signs
        bracket = int(degree_in_sign / 6)
        if bracket > 4:
            bracket = 4
    else:
        # Reversed order for even signs
        bracket = 4 - int(degree_in_sign / 6)
        if bracket < 0:
            bracket = 0

    name = AVASTHA_NAMES[bracket]
    return name, AVASTHA_STRENGTH[name]


def avastha_score_for_planets(
    longitudes: dict[str, float],
    relevant_planets: set[str],
) -> float:
    """Compute aggregate avastha strength for relevant planets.

    Yuva (adult) = 1.0 baseline. Deviations from 1.0 become bonuses/penalties.
    Returns roughly [-0.5, +0.3] — Yuva is neutral (0), Bala/Mrita penalize.
    """
    if not relevant_planets:
        return 0.0

    total = 0.0
    count = 0
    for planet in relevant_planets:
        if planet not in longitudes:
            continue
        _, strength = compute_avastha(longitudes[planet])
        # Center around 1.0 (Yuva baseline)
        total += (strength - 0.6) * 0.5  # scaled so Yuva→+0.2, Mrita→-0.25
        count += 1

    return round(total, 3) if count > 0 else 0.0


# ── Pushkara Navamsa & Pushkara Bhaga ──
# Specific navamsa divisions and degrees that are considered
# extremely auspicious. Moon or Lagna in Pushkara = excellent muhurtha.

# Pushkara Navamsas: specific navamsa padas that are blessed
# Format: sign_index -> set of navamsa numbers (1-9) that are Pushkara
PUSHKARA_NAVAMSA: dict[int, set[int]] = {
    0:  {2, 6},   # Aries
    1:  {4, 8},   # Taurus
    2:  {3, 7},   # Gemini
    3:  {1, 5, 9},# Cancer
    4:  {2, 6},   # Leo
    5:  {4, 8},   # Virgo
    6:  {3, 7},   # Libra
    7:  {1, 5, 9},# Scorpio
    8:  {2, 6},   # Sagittarius
    9:  {4, 8},   # Capricorn
    10: {3, 7},   # Aquarius
    11: {1, 5, 9},# Pisces
}

# Pushkara Bhagas: specific degrees in each sign
# Source: Muhurtha Chintamani
PUSHKARA_BHAGA: dict[int, set[int]] = {
    0:  {21},  # Aries: 21°
    1:  {14},  # Taurus: 14°
    2:  {18},  # Gemini: 18°
    3:  {8},   # Cancer: 8°
    4:  {19},  # Leo: 19°
    5:  {9},   # Virgo: 9°
    6:  {24},  # Libra: 24°
    7:  {11},  # Scorpio: 11°
    8:  {23},  # Sagittarius: 23°
    9:  {14},  # Capricorn: 14°
    10: {19},  # Aquarius: 19°
    11: {9},   # Pisces: 9°
}


def is_pushkara_navamsa(longitude: float) -> bool:
    """Check if a planet/point is in a Pushkara Navamsa."""
    sign_index = int(longitude / 30) % 12
    degree_in_sign = longitude % 30
    navamsa_num = int(degree_in_sign / (30.0 / 9)) + 1
    if navamsa_num > 9:
        navamsa_num = 9
    return navamsa_num in PUSHKARA_NAVAMSA.get(sign_index, set())


def is_pushkara_bhaga(longitude: float) -> bool:
    """Check if a planet/point is at a Pushkara Bhaga degree."""
    sign_index = int(longitude / 30) % 12
    degree = int(longitude % 30)
    return degree in PUSHKARA_BHAGA.get(sign_index, set())


def pushkara_bonus(moon_longitude: float, lagna_longitude: float) -> float:
    """Score bonus if Moon or Lagna is in Pushkara Navamsa/Bhaga.

    Pushkara positions are considered extremely auspicious for muhurtha.
    Returns 0.0 to +0.8.
    """
    bonus = 0.0
    if is_pushkara_navamsa(moon_longitude):
        bonus += 0.3
    if is_pushkara_bhaga(moon_longitude):
        bonus += 0.2
    if is_pushkara_navamsa(lagna_longitude):
        bonus += 0.2
    if is_pushkara_bhaga(lagna_longitude):
        bonus += 0.1
    return round(bonus, 3)


# ── Transit Speed Weighting ──
# A planet that is stationary (about to go retrograde or direct)
# has maximum influence. Classical Vedic astrology considers
# stationary planets as exceptionally powerful.

# Average daily speeds in degrees
AVERAGE_SPEEDS: dict[str, float] = {
    "Sun":     1.0,
    "Moon":    13.2,
    "Mars":    0.52,
    "Mercury": 1.38,
    "Jupiter": 0.083,
    "Venus":   1.2,
    "Saturn":  0.034,
}


def transit_speed_weight(planet: str, actual_speed: float) -> float:
    """Weight a transit's effect based on the planet's current speed.

    Stationary (speed near 0): strongest effect → weight up to 1.5
    Normal speed: weight 1.0
    Very fast: slightly reduced weight → 0.85

    Only meaningful for Mars through Saturn (Sun/Moon are never retrograde).
    """
    avg = AVERAGE_SPEEDS.get(planet, 1.0)
    if avg <= 0:
        return 1.0

    speed_ratio = abs(actual_speed) / avg

    if speed_ratio < 0.1:
        # Nearly stationary — maximum power
        return 1.5
    elif speed_ratio < 0.3:
        # Very slow — strong
        return 1.3
    elif speed_ratio < 0.7:
        # Moderately slow
        return 1.1
    elif speed_ratio > 1.5:
        # Very fast — slightly reduced
        return 0.85
    else:
        return 1.0
