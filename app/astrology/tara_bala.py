"""
Tara Bala — Nakshatra Transit Strength.

Classical system from Muhurtha Chintamani / Brihat Parashara Hora Shastra.
Evaluates the transit Moon's nakshatra relative to the birth nakshatra.

The 27 nakshatras are divided into 9 groups of 3 (Taras).
Each Tara has a specific nature — some are favourable, some are not.

This is one of the 5 classical Pancha-anga Shuddhi checks for muhurtha.
"""

from __future__ import annotations

from app.core.enums import NAKSHATRAS

# The 9 Taras and their nature
# Tara 1: Janma (Birth)   — Bad
# Tara 2: Sampat (Wealth)  — Good
# Tara 3: Vipat (Danger)   — Bad
# Tara 4: Kshema (Wellbeing) — Good
# Tara 5: Pratyari (Obstacle) — Bad
# Tara 6: Sadhaka (Achievement) — Good
# Tara 7: Vadha (Death/Harm)  — Bad
# Tara 8: Mitra (Friend)      — Good
# Tara 9: Parama Mitra (Best Friend) — Good

TARA_NAMES = [
    "Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
    "Sadhaka", "Vadha", "Mitra", "ParamaMitra",
]

TARA_NATURE: dict[str, str] = {
    "Janma":      "bad",
    "Sampat":     "good",
    "Vipat":      "bad",
    "Kshema":     "good",
    "Pratyari":   "bad",
    "Sadhaka":    "good",
    "Vadha":      "bad",
    "Mitra":      "good",
    "ParamaMitra": "good",
}

TARA_SCORE: dict[str, float] = {
    "Janma":      -0.6,
    "Sampat":      0.6,
    "Vipat":      -0.8,
    "Kshema":      0.8,
    "Pratyari":   -0.5,
    "Sadhaka":     0.7,
    "Vadha":      -0.9,
    "Mitra":       0.7,
    "ParamaMitra":  0.9,
}


def compute_tara(birth_nakshatra: str, transit_nakshatra: str) -> tuple[str, float]:
    """Compute the Tara (nakshatra transit strength).

    Args:
        birth_nakshatra: The Moon's nakshatra at birth
        transit_nakshatra: The current transit Moon's nakshatra

    Returns:
        (tara_name, tara_score) — name and score value
    """
    if birth_nakshatra not in NAKSHATRAS or transit_nakshatra not in NAKSHATRAS:
        return "Unknown", 0.0

    birth_idx = NAKSHATRAS.index(birth_nakshatra)
    transit_idx = NAKSHATRAS.index(transit_nakshatra)

    # Count from birth nakshatra (1-indexed)
    count = ((transit_idx - birth_idx) % 27) + 1

    # Tara number: (count % 9), with 9 mapping to 9 not 0
    tara_num = count % 9
    if tara_num == 0:
        tara_num = 9

    tara_name = TARA_NAMES[tara_num - 1]
    score = TARA_SCORE.get(tara_name, 0.0)

    return tara_name, score


def chandra_bala(transit_moon_house_from_natal: int) -> float:
    """Chandra Bala — Moon's transit strength for muhurtha timing.

    The Moon transiting certain houses from natal Moon is
    considered strong or weak for initiating activities.

    Good: 1, 3, 6, 7, 10, 11 from natal Moon
    Bad: 2, 5, 8, 9, 12 from natal Moon
    Neutral: 4

    Returns roughly [-0.5, +0.5].
    """
    good_houses = {1, 3, 6, 7, 10, 11}
    bad_houses = {2, 5, 8, 9, 12}

    if transit_moon_house_from_natal in good_houses:
        return 0.4
    elif transit_moon_house_from_natal in bad_houses:
        return -0.4
    else:
        return 0.0
