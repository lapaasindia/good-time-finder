"""
Simplified Ashtakavarga (Eight-source transit strength grid).

Full Ashtakavarga requires computing bindus from all 8 sources
(7 planets + lagna) for each of the 7 planets across 12 signs.

This module implements a practical approximation: it uses fixed
contribution tables and the natal planet positions to compute
a Sarvashtakavarga-like bindu score for each sign.

Returns a score 0–8 per sign per planet. Higher = stronger transit.
"""

from __future__ import annotations

from app.core.enums import ZODIAC_SIGNS

BENEFIC_OFFSETS: dict[str, list[int]] = {
    "Sun":     [1, 2, 4, 7, 8, 9, 10, 11],
    "Moon":    [1, 3, 6, 7, 10, 11],
    "Mars":    [1, 2, 4, 7, 8, 10, 11],
    "Mercury": [1, 2, 4, 6, 8, 10, 11],
    "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
    "Venus":   [1, 2, 3, 4, 5, 8, 9, 10, 11],
    "Saturn":  [3, 5, 6, 11],
}


def _sign_index(sign: str) -> int:
    return ZODIAC_SIGNS.index(sign)


def compute_planet_bindus(
    planet: str,
    natal_planet_signs: dict[str, str],
    lagna_sign: str,
) -> dict[str, int]:
    offsets = BENEFIC_OFFSETS.get(planet, [])
    bindus: dict[str, int] = {s: 0 for s in ZODIAC_SIGNS}

    sources = list(natal_planet_signs.values()) + [lagna_sign]

    for source_sign in sources:
        source_idx = _sign_index(source_sign)
        for offset in offsets:
            target_idx = (source_idx + offset - 1) % 12
            target_sign = ZODIAC_SIGNS[target_idx]
            bindus[target_sign] += 1

    return bindus


def transit_strength(
    planet: str,
    transit_sign: str,
    natal_planet_signs: dict[str, str],
    lagna_sign: str,
) -> int:
    bindus = compute_planet_bindus(planet, natal_planet_signs, lagna_sign)
    return bindus.get(transit_sign, 0)


def ashtakavarga_bonus(
    current_planet_signs: dict[str, str],
    natal_planet_signs: dict[str, str],
    lagna_sign: str,
) -> float:
    total = 0.0
    count = 0
    for planet, sign in current_planet_signs.items():
        if planet in BENEFIC_OFFSETS:
            score = transit_strength(planet, sign, natal_planet_signs, lagna_sign)
            total += score
            count += 1
    if count == 0:
        return 0.0
    avg = total / count
    normalized = (avg - 4.0) / 4.0
    return round(normalized, 3)
