"""
Nadi Astrology & Trine Linkages Module.
Bhrigu Nadi astrology relies heavily on planetary combinations via trines (1, 5, 9 axis)
and adjacencies (2, 12 axis).
"""
from __future__ import annotations

from typing import Any

def _get_trine_houses(house: int) -> set[int]:
    """Return the houses that are in trine (1, 5, 9) to the given house."""
    h5 = ((house + 4 - 1) % 12) + 1
    h9 = ((house + 8 - 1) % 12) + 1
    return {house, h5, h9}

def _get_adjacent_houses(house: int) -> set[int]:
    """Return houses 2nd and 12th from the given house."""
    h2 = ((house + 1 - 1) % 12) + 1
    h12 = ((house - 1 - 1) % 12) + 1
    return {h2, h12}

def compute_nadi_linkages(planet_houses: dict[str, int]) -> dict[str, dict[str, list[str]]]:
    """
    Computes which planets are linked via Trine (1-5-9) or Adjacency (2-12).
    In Nadi astrology, planets in trine to each other act as if they are conjunct.
    Planets in the 2nd house modify the results, and 12th house causes loss/past.
    """
    linkages = {p: {"trine": [], "next": [], "prev": []} for p in planet_houses}
    
    for p1, h1 in planet_houses.items():
        trines = _get_trine_houses(h1)
        next_h = ((h1 + 1 - 1) % 12) + 1
        prev_h = ((h1 - 1 - 1) % 12) + 1
        
        for p2, h2 in planet_houses.items():
            if p1 == p2:
                continue
            if h2 in trines:
                linkages[p1]["trine"].append(p2)
            if h2 == next_h:
                linkages[p1]["next"].append(p2)
            if h2 == prev_h:
                linkages[p1]["prev"].append(p2)
                
    return linkages

def nadi_career_signature(nadi_links: dict[str, dict[str, list[str]]]) -> list[str]:
    """
    In Nadi, Saturn represents Karma (Profession).
    Planets linked (conjunct/trine) to Saturn determine the career.
    """
    if "Saturn" not in nadi_links:
        return []
        
    saturn_links = nadi_links["Saturn"]["trine"] + nadi_links["Saturn"]["next"]
    signatures = []
    
    if "Jupiter" in saturn_links:
        signatures.append("Respected profession, teaching, advising, law, or management.")
    if "Mars" in saturn_links:
        signatures.append("Engineering, machinery, police, armed forces, or real estate.")
    if "Mercury" in saturn_links:
        signatures.append("Business, accounting, IT, trading, or communication.")
    if "Venus" in saturn_links:
        signatures.append("Luxury, arts, finance, media, or female-oriented products.")
    if "Sun" in saturn_links:
        signatures.append("Government, administration, politics, or leadership roles.")
    if "Moon" in saturn_links:
        signatures.append("Travel, liquids, food, public relations, or shifting careers.")
    if "Rahu" in saturn_links:
        signatures.append("Foreign connections, shadow industries, mass scale, or technology.")
    if "Ketu" in saturn_links:
        signatures.append("Research, occult, medical, obscure fields, or breaks in career.")
        
    return signatures
