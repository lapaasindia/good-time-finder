"""
Vimshottari Dasha system.

Computes Mahadasha, Antardasha, and Pratyantardasha periods
from a person's natal Moon nakshatra position.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterator

from dateutil.relativedelta import relativedelta

DASHA_YEARS: dict[str, int] = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

DASHA_ORDER = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury",
]

TOTAL_YEARS = 120

NAKSHATRA_LORD = {
    "Ashwini": "Ketu",
    "Bharani": "Venus",
    "Krittika": "Sun",
    "Rohini": "Moon",
    "Mrigashira": "Mars",
    "Ardra": "Rahu",
    "Punarvasu": "Jupiter",
    "Pushya": "Saturn",
    "Ashlesha": "Mercury",
    "Magha": "Ketu",
    "Purva Phalguni": "Venus",
    "Uttara Phalguni": "Sun",
    "Hasta": "Moon",
    "Chitra": "Mars",
    "Swati": "Rahu",
    "Vishakha": "Jupiter",
    "Anuradha": "Saturn",
    "Jyeshtha": "Mercury",
    "Mula": "Ketu",
    "Purva Ashadha": "Venus",
    "Uttara Ashadha": "Sun",
    "Shravana": "Moon",
    "Dhanishta": "Mars",
    "Shatabhisha": "Rahu",
    "Purva Bhadrapada": "Jupiter",
    "Uttara Bhadrapada": "Saturn",
    "Revati": "Mercury",
}


@dataclass
class DashaPeriod:
    planet: str
    start: datetime
    end: datetime
    level: str
    parent_planet: str | None = None
    grandparent_planet: str | None = None

    @property
    def duration_days(self) -> float:
        return (self.end - self.start).total_seconds() / 86400


def _fraction_elapsed_in_nakshatra(moon_lon: float) -> float:
    nak_span = 360.0 / 27.0
    position_in_nak = moon_lon % nak_span
    return position_in_nak / nak_span


def _years_to_relativedelta(years: float) -> relativedelta:
    total_days = years * 365.25
    full_years = int(years)
    remaining_days = (years - full_years) * 365.25
    full_months = int(remaining_days / 30.4375)
    remaining_days2 = remaining_days - full_months * 30.4375
    return relativedelta(years=full_years, months=full_months, days=int(remaining_days2))


def compute_mahadashas(
    birth_dt: datetime,
    natal_nakshatra: str,
    natal_moon_longitude: float,
) -> list[DashaPeriod]:
    lord = NAKSHATRA_LORD[natal_nakshatra]
    lord_index = DASHA_ORDER.index(lord)
    lord_years = DASHA_YEARS[lord]
    fraction_elapsed = _fraction_elapsed_in_nakshatra(natal_moon_longitude)
    years_already_elapsed = lord_years * fraction_elapsed
    years_remaining_in_first = lord_years - years_already_elapsed

    remaining_days = years_remaining_in_first * 365.25
    from datetime import timedelta
    start = birth_dt

    periods: list[DashaPeriod] = []

    first_end = start + timedelta(days=remaining_days)
    periods.append(DashaPeriod(
        planet=lord,
        start=start,
        end=first_end,
        level="mahadasha",
    ))

    cur = first_end
    for i in range(1, 9):
        next_lord = DASHA_ORDER[(lord_index + i) % 9]
        dur_days = DASHA_YEARS[next_lord] * 365.25
        end = cur + timedelta(days=dur_days)
        periods.append(DashaPeriod(
            planet=next_lord,
            start=cur,
            end=end,
            level="mahadasha",
        ))
        cur = end

    return periods


def compute_antardashas(mahadasha: DashaPeriod) -> list[DashaPeriod]:
    maha_planet = mahadasha.planet
    maha_duration_days = (mahadasha.end - mahadasha.start).total_seconds() / 86400
    maha_years = DASHA_YEARS[maha_planet]

    start_index = DASHA_ORDER.index(maha_planet)
    from datetime import timedelta

    periods: list[DashaPeriod] = []
    cur = mahadasha.start

    for i in range(9):
        antar_planet = DASHA_ORDER[(start_index + i) % 9]
        antar_years = DASHA_YEARS[antar_planet]
        fraction = (maha_years * antar_years) / TOTAL_YEARS
        dur_days = fraction * 365.25
        end = cur + timedelta(days=dur_days)
        periods.append(DashaPeriod(
            planet=antar_planet,
            start=cur,
            end=end,
            level="antardasha",
            parent_planet=maha_planet,
        ))
        cur = end

    return periods


def compute_pratyantardashas(antardasha: DashaPeriod) -> list[DashaPeriod]:
    antar_planet = antardasha.planet
    maha_planet = antardasha.parent_planet or antar_planet
    antar_duration_days = (antardasha.end - antardasha.start).total_seconds() / 86400
    antar_years = DASHA_YEARS[antar_planet]

    start_index = DASHA_ORDER.index(antar_planet)

    periods: list[DashaPeriod] = []
    cur = antardasha.start

    for i in range(9):
        prat_planet = DASHA_ORDER[(start_index + i) % 9]
        prat_years = DASHA_YEARS[prat_planet]
        fraction = (antar_years * prat_years) / TOTAL_YEARS
        dur_days = (fraction / sum(
            DASHA_YEARS[DASHA_ORDER[(start_index + j) % 9]] for j in range(9)
        )) * antar_duration_days * 9
        end = cur + timedelta(days=dur_days)
        periods.append(DashaPeriod(
            planet=prat_planet,
            start=cur,
            end=end,
            level="pratyantardasha",
            parent_planet=antar_planet,
            grandparent_planet=maha_planet,
        ))
        cur = end

    return periods


def get_active_dasha(
    mahadashas: list[DashaPeriod],
    dt: datetime,
) -> tuple[DashaPeriod | None, DashaPeriod | None]:
    # Ensure dt is offset-aware for comparison
    if dt.tzinfo is None:
        from datetime import timezone
        dt = dt.replace(tzinfo=timezone.utc)
    
    active_maha: DashaPeriod | None = None
    for m in mahadashas:
        # Normalize m.start and m.end to be offset-aware if they aren't
        m_start = m.start if m.start.tzinfo else m.start.replace(tzinfo=timezone.utc)
        m_end = m.end if m.end.tzinfo else m.end.replace(tzinfo=timezone.utc)
        if m_start <= dt < m_end:
            active_maha = m
            break

    if active_maha is None:
        return None, None

    antardashas = compute_antardashas(active_maha)
    active_antar: DashaPeriod | None = None
    for a in antardashas:
        a_start = a.start if a.start.tzinfo else a.start.replace(tzinfo=timezone.utc)
        a_end = a.end if a.end.tzinfo else a.end.replace(tzinfo=timezone.utc)
        if a_start <= dt < a_end:
            active_antar = a
            break

    return active_maha, active_antar


def get_active_dasha_full(
    mahadashas: list[DashaPeriod],
    dt: datetime,
) -> tuple[DashaPeriod | None, DashaPeriod | None, DashaPeriod | None]:
    # Ensure dt is offset-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    active_maha, active_antar = get_active_dasha(mahadashas, dt)

    if active_antar is None:
        return active_maha, active_antar, None

    pratyantardashas = compute_pratyantardashas(active_antar)
    active_prat: DashaPeriod | None = None
    for p in pratyantardashas:
        p_start = p.start if p.start.tzinfo else p.start.replace(tzinfo=timezone.utc)
        p_end = p.end if p.end.tzinfo else p.end.replace(tzinfo=timezone.utc)
        if p_start <= dt < p_end:
            active_prat = p
            break

    return active_maha, active_antar, active_prat


# Expansion: Venus is a major career planet for arts, entertainment, and luxury.
CAREER_PLANETS = {"Sun", "Mercury", "Jupiter", "Saturn", "Venus"}
FINANCE_PLANETS = {"Jupiter", "Venus", "Mercury", "Moon"}
HEALTH_PLANETS = {"Sun", "Moon", "Mars", "Jupiter"}
MARRIAGE_PLANETS = {"Venus", "Moon", "Jupiter", "Mars"}
EDUCATION_PLANETS = {"Mercury", "Jupiter", "Venus"}
SPIRITUALITY_PLANETS = {"Jupiter", "Ketu", "Saturn", "Sun"}
PROPERTY_PLANETS = {"Moon", "Mars", "Saturn", "Venus"}
CHILDREN_PLANETS = {"Jupiter", "Moon", "Venus"}
LEGAL_PLANETS = {"Saturn", "Mars", "Sun", "Jupiter"}
FAME_PLANETS = {"Sun", "Jupiter", "Venus", "Moon"}
RELATIONSHIPS_PLANETS = {"Venus", "Moon", "Jupiter", "Mercury"}
BUSINESS_PLANETS = {"Mercury", "Jupiter", "Saturn", "Sun", "Mars"}
ACCIDENTS_PLANETS = {"Mars", "Saturn", "Rahu", "Ketu"}

# Sign lord mapping (ruler of each zodiac sign)
SIGN_LORD: dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Houses that are GOOD for each life category
GOOD_HOUSES_FOR_CATEGORY: dict[str, set[int]] = {
    "career":      {1, 2, 5, 9, 10, 11},
    "finance":     {2, 5, 9, 11},
    "health":      {1, 5, 9, 11},
    "marriage":    {1, 5, 7, 9, 11},
    "education":   {2, 4, 5, 9, 11},
    "spirituality":{5, 9, 12},
    "property":    {4, 9, 11},
    "children":    {5, 9, 11},
    "legal":       {6, 9, 10, 11},
    "fame":        {1, 5, 9, 10, 11},
    "relationships":{5, 7, 9, 11},
    "business":    {1, 2, 7, 10, 11},
    "accidents":   {6, 8, 12},
    "travel":      {3, 9, 12},
    "general":     {1, 5, 9, 10, 11},
}

# Houses that are BAD for each life category
BAD_HOUSES_FOR_CATEGORY: dict[str, set[int]] = {
    "career":      {6, 8, 12},
    "finance":     {6, 8, 12},
    "health":      {6, 8, 12},
    "marriage":    {6, 8, 12},
    "education":   {6, 8, 12},
    "spirituality":{3, 6},
    "property":    {6, 8, 12},
    "children":    {6, 8, 12},
    "legal":       {8, 12},
    "fame":        {6, 8, 12},
    "relationships":{6, 8, 12},
    "business":    {6, 8, 12},
    "accidents":   {1, 5, 9, 11},
    "travel":      {8},
    "general":     {6, 8, 12},
}


# Maraka houses (death-dealing in Vedic astrology): 2nd and 7th house lords
# Trik houses (evil): 6th, 8th, 12th
# Neutral houses: 3rd (mild malefic), 11th (gains but also greed)
MARAKA_HOUSES = {2, 7}
TRIK_HOUSES = {6, 8, 12}
MILD_MALEFIC_HOUSES = {3}


def house_lordship_score(planet: str, lagna: str, category: str) -> float:
    """Score a planet based on the houses it rules from lagna for a category.

    Uses standard Vedic house significations:
    - Kendra lords (1,4,7,10): generally positive
    - Trikona lords (1,5,9): very positive
    - Trik lords (6,8,12): negative
    - Maraka lords (2,7): negative, especially for health
    """
    from app.core.enums import ZODIAC_SIGNS
    if not lagna or lagna not in ZODIAC_SIGNS:
        return 0.0

    lagna_idx = ZODIAC_SIGNS.index(lagna)
    good_houses = GOOD_HOUSES_FOR_CATEGORY.get(category, set())
    bad_houses = BAD_HOUSES_FOR_CATEGORY.get(category, set())

    # Find which houses this planet rules from lagna
    ruled_houses = []
    for sign, lord in SIGN_LORD.items():
        if lord == planet:
            sign_idx = ZODIAC_SIGNS.index(sign)
            house = ((sign_idx - lagna_idx) % 12) + 1
            ruled_houses.append(house)

    if not ruled_houses:
        return 0.0  # Rahu/Ketu don't own signs

    score = 0.0
    for h in ruled_houses:
        if h in good_houses:
            score += 0.5
        elif h in bad_houses:
            score -= 0.5
        
        # Additional Maraka penalty for health-related categories
        if h in MARAKA_HOUSES:
            if category == 'health':
                score -= 0.4  # Strong penalty for maraka in health
            else:
                score -= 0.15  # Mild penalty for maraka in other areas
        
        # Trikona bonus (strongest positive houses)
        if h in {5, 9}:
            score += 0.3

    return round(score, 3)


CATEGORY_PLANETS: dict[str, set[str]] = {
    "career": CAREER_PLANETS,
    "finance": FINANCE_PLANETS,
    "health": HEALTH_PLANETS,
    "marriage": MARRIAGE_PLANETS,
    "education": EDUCATION_PLANETS,
    "spirituality": SPIRITUALITY_PLANETS,
    "property": PROPERTY_PLANETS,
    "children": CHILDREN_PLANETS,
    "legal": LEGAL_PLANETS,
    "fame": FAME_PLANETS,
    "relationships": RELATIONSHIPS_PLANETS,
    "business": BUSINESS_PLANETS,
    "accidents": ACCIDENTS_PLANETS,
    "travel": {"Mercury", "Moon", "Venus"},
    "general": {"Jupiter", "Moon", "Sun", "Venus"},
}

MALEFIC_CATEGORY_PLANETS: dict[str, set[str]] = {
    "career":      {"Rahu", "Ketu"},
    "finance":     {"Saturn", "Ketu", "Rahu"},
    "health":      {"Saturn", "Rahu", "Ketu"},
    "marriage":    {"Saturn", "Rahu", "Ketu", "Mars"},
    "education":   {"Rahu", "Ketu", "Mars"},
    "spirituality": {"Venus", "Mars"},
    "property":    {"Rahu", "Ketu"},
    "children":    {"Saturn", "Rahu", "Ketu"},
    "legal":       {"Rahu", "Ketu", "Venus"},
    "fame":        {"Saturn", "Rahu", "Ketu"},
    "relationships": {"Saturn", "Rahu", "Ketu", "Mars"},
    "business":    {"Rahu", "Ketu"},
    "accidents":   {"Jupiter", "Venus"},
    "travel":      {"Saturn", "Ketu"},
    "general":     {"Rahu", "Ketu"},
}

# Functional Benefics per Lagna (Ascendant)
# These planets are naturally good for the specific Lagna, regardless of their nature.
FUNCTIONAL_BENEFICS: dict[str, set[str]] = {
    "Aries": {"Sun", "Moon", "Mars", "Jupiter"},
    "Taurus": {"Sun", "Mercury", "Venus", "Saturn"},
    "Gemini": {"Venus", "Mercury"},
    "Cancer": {"Moon", "Mars", "Jupiter"},
    "Leo": {"Sun", "Mars", "Jupiter"},
    "Virgo": {"Mercury", "Venus"},
    "Libra": {"Saturn", "Mercury", "Venus"},
    "Scorpio": {"Moon", "Mars", "Jupiter"},
    "Sagittarius": {"Sun", "Mars", "Jupiter"},
    "Capricorn": {"Mercury", "Venus", "Saturn"},
    "Aquarius": {"Venus", "Saturn"},
    "Pisces": {"Moon", "Mars", "Jupiter"},
}

# Natural planetary friendships for Maha-Antar relationship scoring
PLANET_FRIENDS: dict[str, set[str]] = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
    "Rahu": {"Mercury", "Venus", "Saturn"},
    "Ketu": {"Mars", "Jupiter"},
}

PLANET_ENEMIES: dict[str, set[str]] = {
    "Sun": {"Venus", "Saturn"},
    "Moon": {"Rahu", "Ketu"},
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
    "Rahu": {"Sun", "Moon", "Mars"},
    "Ketu": {"Venus", "Mercury"},
}

# Kendra and Trikona houses — dasha lord placed here natally gives good results
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}


def dasha_bonus_for_category(
    active_maha: DashaPeriod | None,
    active_antar: DashaPeriod | None,
    active_prat: DashaPeriod | None,
    category: str,
    lagna: str | None = None,
    planet_strengths: dict[str, float] | None = None,
    transiting_planets: set[str] | None = None,
    natal_houses: dict[str, int] | None = None,
) -> float:
    """
    Calculate dasha bonus with Vedic astrological principles:
    - House Lordship (which houses the dasha lord rules)
    - Functional benefic consideration
    - Natal planet strength factor (Shadbala)
    - Maha-Antar lord relationship (friendly/enemy)
    - Dasha lord's natal house placement (kendra/trikona = good)
    - Transit-dasha correlation
    """
    if active_maha is None:
        return 0.0

    relevant = CATEGORY_PLANETS.get(category, set())
    malefic = MALEFIC_CATEGORY_PLANETS.get(category, set())
    
    # Lagna-specific functional benefics
    fb = FUNCTIONAL_BENEFICS.get(lagna, set()) if lagna else set()
    
    # Default strengths if not provided
    strengths = planet_strengths or {}
    transiting = transiting_planets or set()
    houses = natal_houses or {}
    
    score = 0.0

    def score_planet(p: str, weight: float, level: str) -> float:
        s = 0.0
        
        # Get natal strength (0.5 to 2.0 typically)
        natal_strength = strengths.get(p, 1.0)
        
        # 1. House Lordship (which houses does this planet rule from lagna?)
        # This is the MOST important factor and gates subsequent bonuses
        lordship = house_lordship_score(p, lagna, category) if lagna else 0.0
        s += lordship * weight
        
        # 2. Functional Benefic bonus
        if p in fb:
            s += weight * 1.0 * (natal_strength / 1.0)
        
        # 3. Category Relevance
        if p in relevant:
            s += weight * 0.8 * (natal_strength / 1.0)
        elif p in malefic:
            if p in fb and natal_strength > 1.2:
                s += weight * 0.5
            else:
                s -= weight * (1.0 / max(natal_strength, 0.5))
        
        # 4. Natal house placement of dasha lord
        natal_house = houses.get(p, 0)
        if natal_house in TRIKONA_HOUSES:
            s += weight * 0.4
        elif natal_house in KENDRA_HOUSES:
            s += weight * 0.3
        elif natal_house in DUSTHANA_HOUSES:
            s -= weight * 0.3
        
        # 5. Transit-Dasha Correlation
        if p in transiting:
            if s > 0:
                s *= 1.25
            else:
                s *= 1.15
                
        return s

    score += score_planet(active_maha.planet, 1.5, "maha")
    if active_antar:
        score += score_planet(active_antar.planet, 1.0, "antar")
    if active_prat:
        score += score_planet(active_prat.planet, 0.5, "prat")

    # 6. Maha-Antar lord relationship modifier
    if active_maha and active_antar:
        maha_p = active_maha.planet
        antar_p = active_antar.planet
        if antar_p in PLANET_FRIENDS.get(maha_p, set()):
            score += 0.5
        elif antar_p in PLANET_ENEMIES.get(maha_p, set()):
            score -= 0.5

    # 7. Antar-Prat lord relationship (finer timing)
    if active_antar and active_prat:
        antar_p = active_antar.planet
        prat_p = active_prat.planet
        if prat_p in PLANET_FRIENDS.get(antar_p, set()):
            score += 0.25
        elif prat_p in PLANET_ENEMIES.get(antar_p, set()):
            score -= 0.25

    return round(score, 3)
