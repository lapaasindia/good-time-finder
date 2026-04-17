"""
Drishti (Aspects) Module.
Calculates Parashari aspects between planets and houses.
"""
from __future__ import annotations
from collections import defaultdict

def _calculate_target_house(source_house: int, aspect_offset: int) -> int:
    """Calculates the target house (1-12) given a source house and a 1-based offset."""
    target = (source_house + aspect_offset - 1) % 12
    return 12 if target == 0 else target

def compute_aspects(planet_houses: dict[str, int]) -> tuple[dict[int, set[str]], dict[str, set[str]]]:
    """
    Compute which planets aspect which houses, and which planets aspect which other planets.
    Returns:
        house_aspects: dict[house_number, set[planet_names]]
        planet_aspects: dict[target_planet, set[source_planet_names]]
    """
    house_aspects = defaultdict(set)
    planet_aspects = defaultdict(set)

    # Standard aspects (1-based counting, so 7th means 6 houses away)
    ASPECT_RULES = {
        "Sun": [7],
        "Moon": [7],
        "Mercury": [7],
        "Venus": [7],
        "Mars": [4, 7, 8],
        "Jupiter": [5, 7, 9],
        "Saturn": [3, 7, 10],
        "Rahu": [5, 7, 9],
        "Ketu": [5, 7, 9]
    }

    # Calculate house aspects
    for planet, house in planet_houses.items():
        if planet not in ASPECT_RULES:
            continue
        for offset in ASPECT_RULES[planet]:
            target_house = _calculate_target_house(house, offset)
            house_aspects[target_house].add(planet)

    # Calculate planet-to-planet aspects
    for target_planet, target_house in planet_houses.items():
        # Any planet that aspects this target's house is aspecting the target planet
        # (excluding itself, though technically a planet doesn't aspect itself anyway)
        aspecting_planets = house_aspects[target_house]
        for aspecting_planet in aspecting_planets:
            if aspecting_planet != target_planet:
                planet_aspects[target_planet].add(aspecting_planet)

    return dict(house_aspects), dict(planet_aspects)
