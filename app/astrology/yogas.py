"""
Yoga detection for natal charts.

A Yoga is a specific planetary combination that indicates
life themes (wealth, career, spirituality, relationships, etc.).

Each yoga returns a YogaResult with name, strength (0–1), and description.
"""

from __future__ import annotations

from dataclasses import dataclass

KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
UPACHAYA_HOUSES = {3, 6, 10, 11}

BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Saturn", "Mars", "Sun", "Rahu", "Ketu"}


@dataclass
class YogaResult:
    name: str
    present: bool
    strength: float
    description: str
    category: str


def _lord_of_house(house: int, lagna: str, planet_signs: dict[str, str]) -> str | None:
    from app.core.enums import ZODIAC_SIGNS
    sign_index = ZODIAC_SIGNS.index(lagna)
    target_sign = ZODIAC_SIGNS[(sign_index + house - 1) % 12]

    SIGN_LORD: dict[str, str] = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
        "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
        "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
        "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
    }
    return SIGN_LORD.get(target_sign)


def detect_raja_yoga(
    planet_houses: dict[str, int],
    lagna: str,
    planet_signs: dict[str, str],
) -> YogaResult:
    kendra_lords = {_lord_of_house(h, lagna, planet_signs) for h in KENDRA_HOUSES}
    trikona_lords = {_lord_of_house(h, lagna, planet_signs) for h in TRIKONA_HOUSES}
    kendra_lords.discard(None)
    trikona_lords.discard(None)

    conjunctions = 0
    for planet, house in planet_houses.items():
        for other_planet, other_house in planet_houses.items():
            if planet != other_planet and house == other_house:
                if planet in kendra_lords and other_planet in trikona_lords:
                    conjunctions += 1

    present = conjunctions > 0
    strength = min(1.0, conjunctions * 0.4)
    return YogaResult(
        name="RajaYoga",
        present=present,
        strength=strength,
        description=(
            "Kendra and Trikona lords conjunct — indicates power, status, and authority."
        ),
        category="career",
    )


def detect_dhana_yoga(
    planet_houses: dict[str, int],
    lagna: str,
    planet_signs: dict[str, str],
) -> YogaResult:
    lord2 = _lord_of_house(2, lagna, planet_signs)
    lord11 = _lord_of_house(11, lagna, planet_signs)

    if lord2 and lord11 and lord2 in planet_houses and lord11 in planet_houses:
        house2 = planet_houses[lord2]
        house11 = planet_houses[lord11]
        conjunct = house2 == house11
        mutual_aspect = abs(house2 - house11) in {7}
        present = conjunct or mutual_aspect
        strength = 0.8 if conjunct else (0.5 if mutual_aspect else 0.0)
    else:
        present = False
        strength = 0.0

    return YogaResult(
        name="DhanaYoga",
        present=present,
        strength=strength,
        description="Lords of 2nd and 11th conjunct or in mutual aspect — wealth accumulation.",
        category="finance",
    )


def detect_gajakesari_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    jup_house = planet_houses.get("Jupiter")
    moon_house = planet_houses.get("Moon")
    if jup_house is None or moon_house is None:
        return YogaResult("GajaKesariYoga", False, 0.0, "", "general")

    diff = abs(jup_house - moon_house)
    if diff > 6:
        diff = 12 - diff

    present = jup_house in KENDRA_HOUSES or diff in {0, 3, 6, 9}
    strength = 0.9 if present else 0.0
    return YogaResult(
        name="GajaKesariYoga",
        present=present,
        strength=strength,
        description="Jupiter in Kendra from Moon — intelligence, fame, and good fortune.",
        category="general",
    )


def detect_hamsa_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
) -> YogaResult:
    jup_sign = planet_signs.get("Jupiter", "")
    jup_house = planet_houses.get("Jupiter", 0)
    from app.astrology.shadbala import OWN_SIGNS, EXALTATION_SIGN
    own = OWN_SIGNS.get("Jupiter", [])
    exalt = EXALTATION_SIGN.get("Jupiter", "")
    in_own_or_exalt = jup_sign in own or jup_sign == exalt
    in_kendra = jup_house in KENDRA_HOUSES
    present = in_own_or_exalt and in_kendra
    strength = 1.0 if present else 0.0
    return YogaResult(
        name="HamsaYoga",
        present=present,
        strength=strength,
        description="Jupiter in own/exaltation sign in Kendra — wisdom, spirituality, leadership.",
        category="spirituality",
    )


def detect_malavya_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
) -> YogaResult:
    ven_sign = planet_signs.get("Venus", "")
    ven_house = planet_houses.get("Venus", 0)
    from app.astrology.shadbala import OWN_SIGNS, EXALTATION_SIGN
    own = OWN_SIGNS.get("Venus", [])
    exalt = EXALTATION_SIGN.get("Venus", "")
    present = (ven_sign in own or ven_sign == exalt) and ven_house in KENDRA_HOUSES
    strength = 1.0 if present else 0.0
    return YogaResult(
        name="MalavyaYoga",
        present=present,
        strength=strength,
        description="Venus in own/exaltation in Kendra — luxury, beauty, relationships.",
        category="marriage",
    )


def detect_budha_aditya_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    sun = planet_houses.get("Sun")
    mer = planet_houses.get("Mercury")
    present = sun is not None and mer is not None and sun == mer
    strength = 0.7 if present else 0.0
    return YogaResult(
        name="BudhaAdityaYoga",
        present=present,
        strength=strength,
        description="Sun and Mercury conjunct — intelligence, communication, success in education.",
        category="education",
    )


def detect_chandra_mangal_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    moon = planet_houses.get("Moon")
    mars = planet_houses.get("Mars")
    present = moon is not None and mars is not None and moon == mars
    strength = 0.6 if present else 0.0
    return YogaResult(
        name="ChandraMangalYoga",
        present=present,
        strength=strength,
        description="Moon and Mars conjunct — financial enterprise, business acumen.",
        category="finance",
    )


def detect_sanyasa_yoga(
    planet_houses: dict[str, int],
    lagna: str,
    planet_signs: dict[str, str],
) -> YogaResult:
    ketu_house = planet_houses.get("Ketu", 0)
    saturn_sign = planet_signs.get("Saturn", "")
    from app.astrology.shadbala import EXALTATION_SIGN, OWN_SIGNS
    saturn_strong = (
        saturn_sign in OWN_SIGNS.get("Saturn", []) or
        saturn_sign == EXALTATION_SIGN.get("Saturn", "")
    )
    present = ketu_house in {1, 9, 12} and saturn_strong
    strength = 0.8 if present else 0.0
    return YogaResult(
        name="SanyasaYoga",
        present=present,
        strength=strength,
        description="Ketu in spiritual house + strong Saturn — detachment, spiritual evolution.",
        category="spirituality",
    )


def detect_yogakaraka_yoga(
    planet_houses: dict[str, int],
    lagna: str,
    planet_signs: dict[str, str],
) -> YogaResult:
    # A planet that owns both a Kendra (1,4,7,10) and a Trikona (1,5,9)
    # Aries: None
    # Taurus: Saturn (9, 10)
    # Gemini: None
    # Cancer: Mars (5, 10)
    # Leo: Mars (4, 9)
    # Virgo: None
    # Libra: Saturn (4, 5)
    # Scorpio: None
    # Sagittarius: None
    # Capricorn: Venus (5, 10)
    # Aquarius: Venus (4, 9)
    # Pisces: None
    
    YOGAKARAKAS: dict[str, str] = {
        "Taurus": "Saturn",
        "Cancer": "Mars",
        "Leo": "Mars",
        "Libra": "Saturn",
        "Capricorn": "Venus",
        "Aquarius": "Venus",
    }
    
    yk_planet = YOGAKARAKAS.get(lagna)
    present = False
    strength = 0.0
    if yk_planet and yk_planet in planet_houses:
        house = planet_houses[yk_planet]
        sign = planet_signs.get(yk_planet, "")
        from app.astrology.shadbala import OWN_SIGNS, EXALTATION_SIGN
        is_strong = sign in OWN_SIGNS.get(yk_planet, []) or sign == EXALTATION_SIGN.get(yk_planet, "")
        
        # Yogakaraka is most powerful in Kendra/Trikona or if strong by sign
        if house in KENDRA_HOUSES or house in TRIKONA_HOUSES or is_strong:
            present = True
            strength = 1.0 if (house in KENDRA_HOUSES and is_strong) else 0.7
            
    return YogaResult(
        name="YogakarakaStatus",
        present=present,
        strength=strength,
        description=f"{yk_planet} acts as a Yogakaraka (Kendra+Trikona lord) for {lagna} Lagna.",
        category="career",
    )


def detect_pancha_mahapurusha_yogas(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
) -> list[YogaResult]:
    # Ruchaka (Mars), Bhadra (Mercury), Hamsa (Jupiter), Malavya (Venus), Sasa (Saturn)
    # Condition: Planet in own sign or exalted AND in a Kendra house (1,4,7,10)
    results = []
    MAHAPURUSHA = {
        "Mars": ("RuchakaYoga", "Physical strength, leadership, and victory."),
        "Mercury": ("BhadraYoga", "Intelligence, communication, and business acumen."),
        "Jupiter": ("HamsaYoga", "Wisdom, spirituality, and respect."),
        "Venus": ("MalavyaYoga", "Luxury, arts, and relationship success."),
        "Saturn": ("SasaYoga", "Authority, discipline, and long-term success."),
    }
    
    from app.astrology.shadbala import OWN_SIGNS, EXALTATION_SIGN
    
    for planet, (name, desc) in MAHAPURUSHA.items():
        house = planet_houses.get(planet)
        sign = planet_signs.get(planet, "")
        if house in KENDRA_HOUSES:
            is_strong = sign in OWN_SIGNS.get(planet, []) or sign == EXALTATION_SIGN.get(planet, "")
            if is_strong:
                # Already have Hamsa and Malavya in detect_all_yogas, but let's make them consistent
                results.append(YogaResult(
                    name=name,
                    present=True,
                    strength=1.2, # Extremely powerful
                    description=desc,
                    category="general" if name != "MalavyaYoga" else "marriage"
                ))
    return results


def detect_all_yogas(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
    lagna: str,
) -> list[YogaResult]:
    basic = [
        detect_raja_yoga(planet_houses, lagna, planet_signs),
        detect_dhana_yoga(planet_houses, lagna, planet_signs),
        detect_gajakesari_yoga(planet_houses),
        detect_budha_aditya_yoga(planet_houses),
        detect_chandra_mangal_yoga(planet_houses),
        detect_sanyasa_yoga(planet_houses, lagna, planet_signs),
        detect_yogakaraka_yoga(planet_houses, lagna, planet_signs),
    ]
    # Add Mahapurusha yogas (Hamsa and Malavya were originally there but now grouped)
    mp = detect_pancha_mahapurusha_yogas(planet_houses, planet_signs)
    return basic + mp


def active_yogas_for_category(
    yogas: list[YogaResult],
    category: str,
) -> list[YogaResult]:
    return [y for y in yogas if y.present and (y.category == category or y.category == "general")]


def yoga_score_for_category(yogas: list[YogaResult], category: str) -> float:
    active = active_yogas_for_category(yogas, category)
    return round(sum(y.strength for y in active), 3)
