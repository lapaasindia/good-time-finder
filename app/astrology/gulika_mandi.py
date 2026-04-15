"""
Gulika (Mandi) — Malefic Sub-planet + Badhaka Lord.

Gulika is a mathematical point derived from Saturn's portion of the day/night.
It is one of the most malefic Upagrahas (sub-planets) in Vedic astrology.

Badhaka is the obstructing sign/lord for each lagna. The Badhaka lord
placed in bad houses or afflicting key planets creates obstacles.

Sources: Brihat Parashara Hora Shastra (BPHS), Phaladeepika.
"""

from __future__ import annotations

from app.core.enums import ZODIAC_SIGNS

SIGN_LORD: dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# ── Gulika Calculation ──
# Gulika is Saturn's portion of the day/night divided into 8 parts.
# Each day of the week has a specific order of planetary rulers for each 1/8th.
# Gulika's portion is the one ruled by Saturn.
#
# For simplicity, we approximate Gulika's sign based on Saturn's
# sub-portion of the birth time. In practice, Gulika's longitude
# requires sunrise/sunset times which vary by location.
#
# Simplified: Gulika falls in a specific sign based on weekday + time portion.

# Saturn rules the following 1/8th portion for each weekday (0=Monday):
# Sunday: 7th portion, Monday: 6th, Tuesday: 5th, Wednesday: 4th,
# Thursday: 3rd, Friday: 2nd, Saturday: 1st
# (Day portions counted from sunrise)

GULIKA_PORTION_BY_WEEKDAY: dict[str, int] = {
    "Sunday":    7,
    "Monday":    6,
    "Tuesday":   5,
    "Wednesday": 4,
    "Thursday":  3,
    "Friday":    2,
    "Saturday":  1,
}


def estimate_gulika_sign(
    weekday: str,
    birth_hour: float,
    lagna: str,
) -> str:
    """Estimate Gulika's sign placement.

    This is a simplified calculation. Full Gulika requires
    exact sunrise time for the birth location and date.

    Uses the approximate method:
    - Divide 24 hours into 8 portions of 3 hours each
    - Saturn's portion for the weekday determines Gulika's time
    - The lagna (rising sign) at Gulika's time determines its sign

    For simplicity, we approximate by counting houses from lagna
    based on the Saturn portion number.
    """
    if lagna not in ZODIAC_SIGNS:
        return ""

    portion = GULIKA_PORTION_BY_WEEKDAY.get(weekday, 4)
    lagna_idx = ZODIAC_SIGNS.index(lagna)

    # Approximate: Gulika sign = portion-th sign from lagna
    gulika_idx = (lagna_idx + portion - 1) % 12
    return ZODIAC_SIGNS[gulika_idx]


def gulika_penalty(
    gulika_sign: str,
    natal_planet_houses: dict[str, int],
    lagna: str,
) -> float:
    """Score the malefic effect of Gulika's placement.

    Gulika in kendra (1,4,7,10): strong negative effect (-0.3)
    Gulika in trikona (5,9): moderate negative (-0.2)
    Gulika in dusthana (6,8,12): less harmful (Viparita effect) (-0.1)
    Gulika in 2,3,11: mild (-0.1)

    Also: Gulika conjunct (same house as) benefics neutralizes some effect.

    Returns 0.0 to -0.4.
    """
    if not gulika_sign or lagna not in ZODIAC_SIGNS:
        return 0.0

    lagna_idx = ZODIAC_SIGNS.index(lagna)
    gulika_idx = ZODIAC_SIGNS.index(gulika_sign) if gulika_sign in ZODIAC_SIGNS else -1
    if gulika_idx < 0:
        return 0.0

    gulika_house = (gulika_idx - lagna_idx) % 12 + 1

    # Base penalty by house
    if gulika_house in {1, 4, 7, 10}:
        penalty = -0.3
    elif gulika_house in {5, 9}:
        penalty = -0.2
    elif gulika_house in {6, 8, 12}:
        penalty = -0.1  # Viparita — less harmful
    else:
        penalty = -0.1

    # Conjunction with benefics reduces penalty
    benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
    for planet in benefics:
        p_house = natal_planet_houses.get(planet, 0)
        if p_house == gulika_house:
            penalty += 0.1  # Benefic conjunction mitigates
            break

    return round(max(-0.4, penalty), 3)


# ── Badhaka (Obstruction) ──
# The Badhaka sign is the sign that causes obstruction for each lagna type:
# - Movable signs (Aries, Cancer, Libra, Capricorn): 11th sign is Badhaka
# - Fixed signs (Taurus, Leo, Scorpio, Aquarius): 9th sign is Badhaka
# - Dual signs (Gemini, Virgo, Sagittarius, Pisces): 7th sign is Badhaka

MOVABLE_SIGNS = {"Aries", "Cancer", "Libra", "Capricorn"}
FIXED_SIGNS = {"Taurus", "Leo", "Scorpio", "Aquarius"}
DUAL_SIGNS = {"Gemini", "Virgo", "Sagittarius", "Pisces"}


def badhaka_sign(lagna: str) -> str:
    """Return the Badhaka sign for the given lagna."""
    if lagna not in ZODIAC_SIGNS:
        return ""

    lagna_idx = ZODIAC_SIGNS.index(lagna)

    if lagna in MOVABLE_SIGNS:
        offset = 10  # 11th house (0-indexed: 10)
    elif lagna in FIXED_SIGNS:
        offset = 8   # 9th house (0-indexed: 8)
    else:  # Dual signs
        offset = 6   # 7th house (0-indexed: 6)

    return ZODIAC_SIGNS[(lagna_idx + offset) % 12]


def badhaka_lord(lagna: str) -> str:
    """Return the lord of the Badhaka sign."""
    b_sign = badhaka_sign(lagna)
    return SIGN_LORD.get(b_sign, "")


def badhaka_penalty(
    lagna: str,
    natal_planet_houses: dict[str, int],
    category: str,
) -> float:
    """Score the Badhaka lord's influence.

    If the Badhaka lord is:
    - In kendra/trikona: can cause obstacles but also eventual gains (-0.15)
    - In dusthana: strong obstruction (-0.25)
    - In 2nd/7th (maraka): dangerous for health (-0.3 for health)

    Returns 0.0 to -0.3.
    """
    b_lord = badhaka_lord(lagna)
    if not b_lord:
        return 0.0

    house = natal_planet_houses.get(b_lord, 0)
    if house == 0:
        return 0.0

    KENDRA = {1, 4, 7, 10}
    TRIKONA = {5, 9}
    DUSTHANA = {6, 8, 12}
    MARAKA = {2, 7}

    penalty = 0.0

    if house in DUSTHANA:
        penalty = -0.2
    elif house in KENDRA:
        penalty = -0.1
    elif house in MARAKA:
        penalty = -0.15
        if category == "health":
            penalty = -0.3  # Badhaka in maraka is dangerous for health
    elif house in TRIKONA:
        penalty = -0.1
    else:
        penalty = -0.05

    return round(penalty, 3)
