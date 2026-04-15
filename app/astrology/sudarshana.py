"""
Sudarshana Chakra — Triple-Perspective Analysis.

The Sudarshana Chakra is a unique Vedic technique that evaluates
transits and houses from THREE reference points simultaneously:
1. Lagna (Ascendant) — physical body, personality, initiative
2. Moon sign — mind, emotions, perception
3. Sun sign — soul, authority, vitality

When a transit is favourable from all three, it is extremely powerful.
When unfavourable from all three, the negativity is amplified.
Mixed results indicate nuanced outcomes.

Source: Brihat Parashara Hora Shastra, Ch. 66.
"""

from __future__ import annotations

from app.core.enums import ZODIAC_SIGNS


def _house_from(transit_sign: str, reference_sign: str) -> int:
    """Compute house number of transit_sign from reference_sign (1-indexed)."""
    if transit_sign not in ZODIAC_SIGNS or reference_sign not in ZODIAC_SIGNS:
        return 0
    ref_idx = ZODIAC_SIGNS.index(reference_sign)
    tr_idx = ZODIAC_SIGNS.index(transit_sign)
    return ((tr_idx - ref_idx) % 12) + 1


# Good transit houses (generic — applies for most planets from any reference)
GENERIC_GOOD_HOUSES = {1, 2, 3, 5, 9, 10, 11}
GENERIC_BAD_HOUSES = {4, 6, 8, 12}


def sudarshana_transit_score(
    transit_sign: str,
    lagna: str,
    moon_sign: str,
    sun_sign: str,
) -> float:
    """Score a transit sign from all three Sudarshana reference points.

    Each reference contributes:
      +0.3 if transit is in a good house from it
      -0.3 if transit is in a bad house from it
      0.0 if in 7th (neutral — can go either way)

    When all three agree, a 1.3× amplification factor applies.

    Returns roughly [-1.2, +1.2].
    """
    scores = []

    for ref_sign, weight in [(lagna, 0.35), (moon_sign, 0.40), (sun_sign, 0.25)]:
        house = _house_from(transit_sign, ref_sign)
        if house == 0:
            scores.append(0.0)
            continue

        if house in GENERIC_GOOD_HOUSES:
            scores.append(weight)
        elif house in GENERIC_BAD_HOUSES:
            scores.append(-weight)
        else:  # 7th house — neutral
            scores.append(0.0)

    total = sum(scores)

    # Amplification: if all three agree on direction, boost
    if all(s > 0 for s in scores):
        total *= 1.3
    elif all(s < 0 for s in scores):
        total *= 1.3

    return round(total, 3)


def sudarshana_aggregate(
    transit_planet_signs: dict[str, str],
    lagna: str,
    moon_sign: str,
    sun_sign: str,
) -> float:
    """Aggregate Sudarshana Chakra score across all transiting planets.

    Heavy planets (Jupiter, Saturn, Rahu, Ketu) count more.
    Returns roughly [-3.0, +3.0].
    """
    PLANET_WEIGHTS = {
        "Jupiter": 1.5,
        "Saturn":  1.3,
        "Rahu":    1.0,
        "Ketu":    1.0,
        "Mars":    0.8,
        "Sun":     0.6,
        "Moon":    0.5,
        "Mercury": 0.4,
        "Venus":   0.4,
    }

    total = 0.0
    for planet, sign in transit_planet_signs.items():
        if sign not in ZODIAC_SIGNS:
            continue
        weight = PLANET_WEIGHTS.get(planet, 0.5)
        s = sudarshana_transit_score(sign, lagna, moon_sign, sun_sign)
        total += s * weight

    # Normalize to a reasonable range
    return round(total * 0.15, 3)
