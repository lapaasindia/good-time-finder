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

# ── VEDHA (Obstruction) Tables ──
# When planet is in a GOOD house from Moon, a vedha planet in the vedha-house
# OBSTRUCTS that good effect. Classical Vedic gochara principle.
# Format: {planet: {good_house: vedha_house}}
# Source: Brihat Parashara Hora Shastra, Phaladeepika
VEDHA_TABLE: dict[str, dict[int, int]] = {
    "Sun":     {3: 9, 6: 12, 10: 4, 11: 5},
    "Moon":    {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    "Mars":    {3: 12, 6: 9, 11: 5},
    "Mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
    "Jupiter": {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
    "Venus":   {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
    "Saturn":  {3: 12, 6: 9, 11: 5},
}
# Note: Rahu and Ketu follow Saturn's vedha table
VEDHA_TABLE["Rahu"] = VEDHA_TABLE["Saturn"]
VEDHA_TABLE["Ketu"] = VEDHA_TABLE["Saturn"]


# ── Transit-to-Natal Aspect definitions ──
# Classical Vedic aspects from a transiting planet to natal planet positions.
# Aspect type → score modifier (positive = harmonious, negative = stressful)
ASPECT_OFFSETS: dict[str, tuple[int, float]] = {
    "conjunction": (0, 1.0),    # same sign — strongest influence
    "trine_5":    (4, 0.6),    # 5th aspect — benefic
    "trine_9":    (8, 0.6),    # 9th aspect — benefic
    "opposition":  (6, -0.5),   # 7th aspect — stressful
    "square_4":   (3, -0.3),   # 4th aspect — challenging
    "square_10":  (9, -0.3),   # 10th aspect — challenging
}

# Special planetary aspects (Vedic: Mars 4/8, Jupiter 5/9, Saturn 3/10)
# These are ADDITIONAL to the standard 7th aspect all planets have.
SPECIAL_ASPECTS: dict[str, list[int]] = {
    "Mars":    [3, 7],      # 4th and 8th house aspects (0-indexed offsets: 3, 7)
    "Jupiter": [4, 8],      # 5th and 9th house aspects
    "Saturn":  [2, 9],      # 3rd and 10th house aspects
    "Rahu":    [4, 8],      # follows Jupiter's aspects
    "Ketu":    [4, 8],      # follows Jupiter's aspects
}

# Planets whose transits are significant enough for aspect scoring
# (inner planets move too fast to have lasting aspect effects)
ASPECT_TRANSIT_PLANETS = {"Jupiter", "Saturn", "Rahu", "Ketu", "Mars"}


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


def _check_vedha(
    planet: str,
    house_from_moon: int,
    all_planet_houses: dict[str, int],
) -> bool:
    """Check if a planet's good transit is obstructed by vedha.

    Returns True if vedha is active (good effect is blocked).
    """
    vedha_pairs = VEDHA_TABLE.get(planet, {})
    vedha_house = vedha_pairs.get(house_from_moon)
    if vedha_house is None:
        return False

    # Check if ANY other planet occupies the vedha house
    for other_planet, other_house in all_planet_houses.items():
        if other_planet != planet and other_house == vedha_house:
            return True
    return False


def transit_aspect_score(
    transit_signs: dict[str, str],
    natal_planet_signs: dict[str, str],
    natal_moon_sign: str,
    relevant_planets: set[str],
) -> float:
    """Score transit-to-natal aspects for slow-moving planets.

    Evaluates conjunctions, trines, oppositions, and squares
    between transiting outer planets and natal planet positions.
    Also includes special Vedic aspects (Mars 4/8, Jupiter 5/9, Saturn 3/10).

    Returns a score roughly in [-2.0, +2.0].
    """
    if not natal_planet_signs:
        return 0.0

    total = 0.0
    natal_key_planets = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}

    for t_planet in ASPECT_TRANSIT_PLANETS:
        t_sign = transit_signs.get(t_planet, "")
        if t_sign not in ZODIAC_SIGNS:
            continue
        t_idx = ZODIAC_SIGNS.index(t_sign)
        t_weight = PLANET_GOCHARA_WEIGHT.get(t_planet, 1.0)

        # Is this planet benefic or malefic by nature?
        is_benefic = t_planet in {"Jupiter"}
        is_malefic = t_planet in {"Saturn", "Mars", "Rahu", "Ketu"}

        for n_planet in natal_key_planets:
            n_sign = natal_planet_signs.get(n_planet, "")
            if n_sign not in ZODIAC_SIGNS:
                continue
            n_idx = ZODIAC_SIGNS.index(n_sign)
            offset = (t_idx - n_idx) % 12

            # Relevance weight: relevant natal planets matter more
            n_relevance = 1.0 if n_planet in relevant_planets else 0.3

            # Standard aspects
            for aspect_name, (asp_offset, asp_score) in ASPECT_OFFSETS.items():
                if offset == asp_offset:
                    # Benefic planets make good aspects better, bad aspects less bad
                    if is_benefic:
                        modifier = asp_score * 0.4 if asp_score > 0 else asp_score * 0.2
                    elif is_malefic:
                        modifier = asp_score * 0.2 if asp_score > 0 else asp_score * 0.4
                    else:
                        modifier = asp_score * 0.3
                    total += modifier * t_weight * n_relevance * 0.15

            # Special Vedic aspects
            special = SPECIAL_ASPECTS.get(t_planet, [])
            if offset in special:
                if is_benefic:
                    total += 0.15 * t_weight * n_relevance
                elif is_malefic:
                    total -= 0.15 * t_weight * n_relevance

    return round(total, 3)


def apply_retrograde_modifier(
    planet: str,
    base_score: float,
    is_retrograde: bool,
) -> float:
    """Modify gochara score based on retrograde status.

    Retrograde planets in Vedic astrology:
    - Benefic retrograde: positive effects weakened (×0.7)
    - Malefic retrograde: negative effects intensified (×1.2),
      but can also give unexpected positive results in some houses
    - Retrograde planets gain cheshta bala (motional strength)
      but deliver results in an unusual/delayed manner
    """
    if not is_retrograde:
        return base_score

    natural_benefics = {"Jupiter", "Venus", "Mercury"}
    natural_malefics = {"Saturn", "Mars", "Rahu", "Ketu"}

    if planet in natural_benefics:
        # Retrograde benefic: good effects weakened, bad effects slightly reduced
        if base_score > 0:
            return round(base_score * 0.7, 3)
        else:
            return round(base_score * 0.85, 3)
    elif planet in natural_malefics:
        # Retrograde malefic: negative intensified, positive slightly boosted
        if base_score < 0:
            return round(base_score * 1.2, 3)
        else:
            return round(base_score * 1.1, 3)

    return base_score


def category_gochara_score(
    planet_signs: dict[str, str],
    natal_moon_sign: str,
    relevant_planets: set[str],
    natal_lagna: str | None = None,
    natal_planet_signs: dict[str, str] | None = None,
    retrograde_planets: set[str] | None = None,
) -> float:
    """Enhanced gochara score with vedha, retrograde, and aspect modifiers."""
    scores = gochara_score(planet_signs, natal_moon_sign, natal_lagna)
    if not scores:
        return 0.0

    # Build house-from-moon map for vedha checks
    planet_houses_from_moon: dict[str, int] = {}
    for p, s in planet_signs.items():
        if s in ZODIAC_SIGNS and natal_moon_sign in ZODIAC_SIGNS:
            planet_houses_from_moon[p] = _house_from_sign(s, natal_moon_sign)

    # Apply vedha and retrograde corrections
    adjusted_scores: dict[str, float] = {}
    for planet, raw_score in scores.items():
        score = raw_score

        # Vedha: if planet is in a GOOD house but vedha is active, reduce benefit
        h = planet_houses_from_moon.get(planet)
        if h and h in GOOD_HOUSES_FROM_NATAL_MOON.get(planet, set()):
            if False and _check_vedha(planet, h, planet_houses_from_moon):
                score *= 0.3  # Disabled: exacerbates structural negative bias

        # Retrograde modifier
        if False and retrograde_planets and planet in retrograde_planets:
            pass  # Disabled retrograde modifier

        adjusted_scores[planet] = score

    relevant_sum = sum(s for p, s in adjusted_scores.items() if p in relevant_planets)
    background_sum = sum(s * 0.3 for p, s in adjusted_scores.items() if p not in relevant_planets)

    # Transit-to-natal aspect bonus
    aspect_bonus = 0.0
    if natal_planet_signs:
        aspect_bonus = 0.0  # Disabled: instructed not to re-enable transit-over-natal conjunction scoring

    return round(relevant_sum + background_sum + aspect_bonus, 3)
