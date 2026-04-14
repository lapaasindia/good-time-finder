"""
Additional natal yoga detectors.

Covers:
- Neecha Bhanga Raja Yoga  — debilitation cancelled, creating a rise
- Viparita Raja Yoga       — lords of dusthana in dusthana (evil cancels evil)
- Full Pancha Mahapurusha  — Ruchaka, Bhadra, Hamsa, Malavya, Shasha (Mars/Mercury/Jupiter/Venus/Saturn)
- Lakshmi Yoga             — Venus + 9th lord strongly placed
- Saraswati Yoga           — Mercury/Venus/Jupiter in Kendra/Trikona
- Chandra-Adhi Yoga        — Benefics in 6th/7th/8th from Moon
- Vesi/Vasi/Ubhayachari    — Planets in 2nd/12th/both from Sun
"""

from __future__ import annotations

from dataclasses import dataclass

from app.astrology.shadbala import OWN_SIGNS, EXALTATION_SIGN, DEBILITATION_SIGN
from app.astrology.yogas import YogaResult, KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES, BENEFICS

SIGN_LORD: dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

EXALTATION_DISPOSITOR: dict[str, str] = {
    planet: SIGN_LORD.get(sign, "") for planet, sign in EXALTATION_SIGN.items()
}


def detect_neecha_bhanga_raja_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
) -> YogaResult:
    cancellations = 0
    for planet, sign in planet_signs.items():
        if sign != DEBILITATION_SIGN.get(planet):
            continue
        dispositor = SIGN_LORD.get(sign, "")
        exalt_dispositor = EXALTATION_DISPOSITOR.get(planet, "")

        dispositor_in_kendra = planet_houses.get(dispositor, 0) in KENDRA_HOUSES
        exalt_lord_in_kendra = planet_houses.get(exalt_dispositor, 0) in KENDRA_HOUSES
        debil_lord_exalted = (
            planet_signs.get(dispositor, "") == EXALTATION_SIGN.get(dispositor, "unknown")
        )

        if dispositor_in_kendra or exalt_lord_in_kendra or debil_lord_exalted:
            cancellations += 1

    present = cancellations > 0
    return YogaResult(
        name="NeechaBhangarajaYoga",
        present=present,
        strength=min(1.0, cancellations * 0.5),
        description=(
            "Debilitation cancelled — planet rises above its weakness, "
            "indicating unexpected success after setbacks."
        ),
        category="career",
    )


def detect_viparita_raja_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
    lagna: str,
) -> YogaResult:
    from app.core.enums import ZODIAC_SIGNS
    lagna_idx = ZODIAC_SIGNS.index(lagna)

    def house_sign(h: int) -> str:
        return ZODIAC_SIGNS[(lagna_idx + h - 1) % 12]

    dusthana_lords = {SIGN_LORD[house_sign(h)] for h in DUSTHANA_HOUSES}

    count = 0
    for lord in dusthana_lords:
        if lord in planet_houses and planet_houses[lord] in DUSTHANA_HOUSES:
            count += 1

    present = count >= 2
    return YogaResult(
        name="ViparitagajaYoga",
        present=present,
        strength=min(1.0, count * 0.4),
        description=(
            "Lords of difficult houses placed in difficult houses — "
            "evil cancels evil, conferring unexpected royal fortune."
        ),
        category="general",
    )


def detect_ruchaka_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
) -> YogaResult:
    mars_sign = planet_signs.get("Mars", "")
    mars_house = planet_houses.get("Mars", 0)
    own = OWN_SIGNS.get("Mars", [])
    exalt = EXALTATION_SIGN.get("Mars", "")
    present = (mars_sign in own or mars_sign == exalt) and mars_house in KENDRA_HOUSES
    return YogaResult(
        name="RuchakaYoga",
        present=present,
        strength=1.0 if present else 0.0,
        description="Mars in own/exalt in Kendra — Pancha Mahapurusha: courage, military, leadership.",
        category="career",
    )


def detect_bhadra_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
) -> YogaResult:
    merc_sign = planet_signs.get("Mercury", "")
    merc_house = planet_houses.get("Mercury", 0)
    own = OWN_SIGNS.get("Mercury", [])
    exalt = EXALTATION_SIGN.get("Mercury", "")
    present = (merc_sign in own or merc_sign == exalt) and merc_house in KENDRA_HOUSES
    return YogaResult(
        name="BhadraYoga",
        present=present,
        strength=1.0 if present else 0.0,
        description="Mercury in own/exalt in Kendra — Pancha Mahapurusha: intelligence, communication.",
        category="education",
    )


def detect_shasha_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
) -> YogaResult:
    sat_sign = planet_signs.get("Saturn", "")
    sat_house = planet_houses.get("Saturn", 0)
    own = OWN_SIGNS.get("Saturn", [])
    exalt = EXALTATION_SIGN.get("Saturn", "")
    present = (sat_sign in own or sat_sign == exalt) and sat_house in KENDRA_HOUSES
    return YogaResult(
        name="ShashaYoga",
        present=present,
        strength=1.0 if present else 0.0,
        description="Saturn in own/exalt in Kendra — Pancha Mahapurusha: discipline, authority, longevity.",
        category="career",
    )


def detect_saraswati_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
) -> YogaResult:
    good_houses = KENDRA_HOUSES | TRIKONA_HOUSES
    jup_ok = planet_houses.get("Jupiter", 0) in good_houses
    ven_ok = planet_houses.get("Venus", 0) in good_houses
    mer_ok = planet_houses.get("Mercury", 0) in good_houses
    count = sum([jup_ok, ven_ok, mer_ok])
    present = count >= 2
    return YogaResult(
        name="SaraswatiYoga",
        present=present,
        strength=min(1.0, count * 0.35),
        description=(
            "Mercury, Venus, and Jupiter in Kendra/Trikona — "
            "exceptional intelligence, creativity, and learning."
        ),
        category="education",
    )


def detect_lakshmi_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
    lagna: str,
) -> YogaResult:
    from app.core.enums import ZODIAC_SIGNS
    lagna_idx = ZODIAC_SIGNS.index(lagna)
    ninth_sign = ZODIAC_SIGNS[(lagna_idx + 8) % 12]
    lord_9 = SIGN_LORD.get(ninth_sign, "")
    lord_9_in_kendra_trikona = planet_houses.get(lord_9, 0) in (KENDRA_HOUSES | TRIKONA_HOUSES)
    venus_own_exalt = (
        planet_signs.get("Venus", "") in OWN_SIGNS.get("Venus", []) or
        planet_signs.get("Venus", "") == EXALTATION_SIGN.get("Venus", "")
    )
    present = lord_9_in_kendra_trikona and venus_own_exalt
    return YogaResult(
        name="LakshmiYoga",
        present=present,
        strength=0.9 if present else 0.0,
        description="9th lord + strong Venus in Kendra/Trikona — goddess of wealth blesses the chart.",
        category="finance",
    )


def detect_chandra_adhi_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    moon_house = planet_houses.get("Moon", 0)
    target_houses = {
        ((moon_house + 5) % 12) + 1,
        ((moon_house + 6) % 12) + 1,
        ((moon_house + 7) % 12) + 1,
    }
    benefic_planets = ["Mercury", "Venus", "Jupiter"]
    count = sum(1 for p in benefic_planets if planet_houses.get(p, 0) in target_houses)
    present = count >= 2
    return YogaResult(
        name="ChandraAdhiYoga",
        present=present,
        strength=min(1.0, count * 0.35),
        description=(
            "Benefics (Mercury/Venus/Jupiter) in 6th/7th/8th from Moon — "
            "protection, rise in life, good health."
        ),
        category="general",
    )


def detect_vesi_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    sun_house = planet_houses.get("Sun", 0)
    second_from_sun = (sun_house % 12) + 1
    benefic_in_second = any(
        planet_houses.get(p, 0) == second_from_sun
        for p in ["Mercury", "Venus", "Jupiter"]
    )
    return YogaResult(
        name="VesiYoga",
        present=benefic_in_second,
        strength=0.7 if benefic_in_second else 0.0,
        description="Benefic in 2nd from Sun — eloquence, wealth, royal disposition.",
        category="general",
    )


def detect_vasi_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    """Benefic planet in 12th from Sun (Phaladeepika Ch.8)."""
    sun_house = planet_houses.get("Sun", 0)
    twelfth_from_sun = ((sun_house - 2) % 12) + 1
    benefic_in_twelfth = any(
        planet_houses.get(p, 0) == twelfth_from_sun
        for p in ["Mercury", "Venus", "Jupiter"]
    )
    return YogaResult(
        name="VasiYoga",
        present=benefic_in_twelfth,
        strength=0.7 if benefic_in_twelfth else 0.0,
        description=(
            "Benefic in 12th from Sun — charitable nature, virtuous conduct, "
            "and high moral standing. Per Phaladeepika, the native gains fame "
            "through righteous deeds."
        ),
        category="general",
    )


def detect_ubhayachari_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    """Benefics on both sides of Sun (2nd + 12th). Brihat Parashara Hora Shastra."""
    sun_house = planet_houses.get("Sun", 0)
    second_from = (sun_house % 12) + 1
    twelfth_from = ((sun_house - 2) % 12) + 1
    has_2nd = any(planet_houses.get(p, 0) == second_from for p in ["Mercury", "Venus", "Jupiter"])
    has_12th = any(planet_houses.get(p, 0) == twelfth_from for p in ["Mercury", "Venus", "Jupiter"])
    present = has_2nd and has_12th
    return YogaResult(
        name="UbhayachariYoga",
        present=present,
        strength=0.85 if present else 0.0,
        description=(
            "Benefics flanking the Sun (2nd and 12th houses from Sun) — "
            "the native is equal to a king, eloquent, generous, and blessed "
            "with comforts. One of the most powerful Solar yogas (BPHS Ch.36)."
        ),
        category="career",
    )


def detect_sunapha_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    """Planet (not Sun/Rahu/Ketu) in 2nd from Moon. Phaladeepika Ch.9."""
    moon_house = planet_houses.get("Moon", 0)
    second_from_moon = (moon_house % 12) + 1
    forming = [p for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
               if planet_houses.get(p, 0) == second_from_moon]
    present = len(forming) > 0
    return YogaResult(
        name="SunaphaYoga",
        present=present,
        strength=min(1.0, len(forming) * 0.4) if present else 0.0,
        description=(
            "Planet in 2nd from Moon — self-made wealth and intelligence. "
            "The native earns through own effort, possesses good reputation "
            "and is equal to a ruler. Forming planets: "
            + (", ".join(forming) if forming else "none") + "."
        ),
        category="finance",
    )


def detect_anapha_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    """Planet (not Sun/Rahu/Ketu) in 12th from Moon. Phaladeepika Ch.9."""
    moon_house = planet_houses.get("Moon", 0)
    twelfth_from_moon = ((moon_house - 2) % 12) + 1
    forming = [p for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
               if planet_houses.get(p, 0) == twelfth_from_moon]
    present = len(forming) > 0
    return YogaResult(
        name="AnaphaYoga",
        present=present,
        strength=min(1.0, len(forming) * 0.4) if present else 0.0,
        description=(
            "Planet in 12th from Moon — powerful personality and strong health. "
            "The native is virtuous, famous, and free from disease. "
            "Forming planets: " + (", ".join(forming) if forming else "none") + "."
        ),
        category="health",
    )


def detect_durudhara_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    """Planets (not Sun/Rahu/Ketu) in both 2nd and 12th from Moon. Phaladeepika."""
    moon_house = planet_houses.get("Moon", 0)
    second_from = (moon_house % 12) + 1
    twelfth_from = ((moon_house - 2) % 12) + 1
    valid = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    has_2nd = any(planet_houses.get(p, 0) == second_from for p in valid)
    has_12th = any(planet_houses.get(p, 0) == twelfth_from for p in valid)
    present = has_2nd and has_12th
    return YogaResult(
        name="DurudharaYoga",
        present=present,
        strength=0.85 if present else 0.0,
        description=(
            "Planets flanking the Moon (2nd + 12th) — the native enjoys "
            "wealth, vehicles, property, and is generous and charitable. "
            "One of the strongest lunar yogas per Phaladeepika."
        ),
        category="finance",
    )


def detect_kemdrum_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    """No planet in 2nd or 12th from Moon (excluding Sun/Rahu/Ketu). An inauspicious yoga."""
    moon_house = planet_houses.get("Moon", 0)
    second_from = (moon_house % 12) + 1
    twelfth_from = ((moon_house - 2) % 12) + 1
    valid = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    has_2nd = any(planet_houses.get(p, 0) == second_from for p in valid)
    has_12th = any(planet_houses.get(p, 0) == twelfth_from for p in valid)
    present = not has_2nd and not has_12th
    return YogaResult(
        name="KemdrumYoga",
        present=present,
        strength=0.7 if present else 0.0,
        description=(
            "No planet adjacent to Moon (2nd/12th) — Kemdrum Dosha. "
            "Per Brihat Jataka, the native may face poverty, loneliness, "
            "and sudden reversals in fortune. Check for cancellation "
            "(Kemdrum Bhanga) via Jupiter's aspect or Moon in Kendra."
        ),
        category="general",
    )


def detect_kemdrum_bhanga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
) -> YogaResult:
    """Cancellation of Kemdrum yoga — Moon in Kendra or aspected by Jupiter."""
    kemdrum = detect_kemdrum_yoga(planet_houses)
    if not kemdrum.present:
        return YogaResult("KemdrumBhanga", False, 0.0,
                          "Kemdrum not present — cancellation not applicable.", "general")
    moon_house = planet_houses.get("Moon", 0)
    jup_house = planet_houses.get("Jupiter", 0)
    moon_in_kendra = moon_house in KENDRA_HOUSES
    jup_aspects_moon = abs(jup_house - moon_house) in {0, 3, 6, 9} or jup_house == moon_house
    cancelled = moon_in_kendra or jup_aspects_moon
    return YogaResult(
        name="KemdrumBhanga",
        present=cancelled,
        strength=0.8 if cancelled else 0.0,
        description=(
            "Kemdrum Yoga cancelled — "
            + ("Moon in Kendra house" if moon_in_kendra else "")
            + (" and " if moon_in_kendra and jup_aspects_moon else "")
            + ("Jupiter aspects Moon" if jup_aspects_moon else "")
            + ". The ill effects of Kemdrum are neutralised; the native "
            "recovers from setbacks and gains unexpected support."
        ),
        category="general",
    )


def detect_amala_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    """Benefic in 10th from Moon or Lagna. BPHS — confers spotless character."""
    moon_house = planet_houses.get("Moon", 0)
    tenth_from_moon = ((moon_house + 8) % 12) + 1
    forming = [p for p in ["Mercury", "Venus", "Jupiter"]
               if planet_houses.get(p, 0) == tenth_from_moon]
    present = len(forming) > 0
    return YogaResult(
        name="AmalaYoga",
        present=present,
        strength=0.8 if present else 0.0,
        description=(
            "Benefic in 10th from Moon — spotless reputation and lasting fame. "
            "Per BPHS, the native's good deeds spread far and wide. "
            "Forming: " + (", ".join(forming) if forming else "none") + "."
        ),
        category="career",
    )


def detect_shakata_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    """Moon in 6th or 8th from Jupiter — an adverse yoga per Phaladeepika."""
    moon_house = planet_houses.get("Moon", 0)
    jup_house = planet_houses.get("Jupiter", 0)
    diff = ((moon_house - jup_house) % 12)
    present = diff in {5, 7}  # 6th or 8th from Jupiter (0-indexed diff)
    return YogaResult(
        name="ShakataYoga",
        present=present,
        strength=0.6 if present else 0.0,
        description=(
            "Moon in 6th or 8th from Jupiter — Shakata (cart) yoga. "
            "The native experiences fluctuating fortune like a wheel — "
            "sometimes up, sometimes down. Per Phaladeepika, wealth is "
            "unstable and there may be ingratitude from others."
        ),
        category="finance",
    )


def detect_guru_mangal_yoga(
    planet_houses: dict[str, int],
) -> YogaResult:
    """Jupiter and Mars conjunct or in mutual aspect — courage with wisdom."""
    jup_house = planet_houses.get("Jupiter", 0)
    mars_house = planet_houses.get("Mars", 0)
    conjunct = jup_house == mars_house
    mutual_aspect = abs(jup_house - mars_house) in {6}  # 7th house aspect (diff=6)
    present = conjunct or mutual_aspect
    strength = 0.8 if conjunct else (0.6 if mutual_aspect else 0.0)
    return YogaResult(
        name="GuruMangalYoga",
        present=present,
        strength=strength,
        description=(
            "Jupiter–Mars conjunction or mutual aspect — combines wisdom "
            "with courage. The native is a natural leader, charitable, "
            "and skilled in law, defence, or administration. "
            "Particularly strong for career and property matters."
        ),
        category="career",
    )


def detect_parivartana_yoga(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
    lagna: str,
) -> YogaResult:
    """Two planets exchange signs (mutual reception). BPHS Ch.28."""
    from app.core.enums import ZODIAC_SIGNS
    exchanges: list[str] = []
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for i, p1 in enumerate(planets):
        for p2 in planets[i + 1:]:
            s1 = planet_signs.get(p1, "")
            s2 = planet_signs.get(p2, "")
            lord_s1 = SIGN_LORD.get(s1, "")
            lord_s2 = SIGN_LORD.get(s2, "")
            if lord_s1 == p2 and lord_s2 == p1:
                exchanges.append(f"{p1}↔{p2}")
    present = len(exchanges) > 0
    return YogaResult(
        name="ParivartanaYoga",
        present=present,
        strength=min(1.0, len(exchanges) * 0.5),
        description=(
            "Mutual sign exchange (Parivartana) — two planets swap signs, "
            "creating a powerful bond between the houses they rule. "
            "Per BPHS, this is equivalent to a conjunction and greatly "
            "strengthens both houses. Exchanges: "
            + (", ".join(exchanges) if exchanges else "none") + "."
        ),
        category="general",
    )


def detect_all_extra_yogas(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
    lagna: str,
) -> list[YogaResult]:
    return [
        detect_neecha_bhanga_raja_yoga(planet_houses, planet_signs),
        detect_viparita_raja_yoga(planet_houses, planet_signs, lagna),
        detect_ruchaka_yoga(planet_houses, planet_signs),
        detect_bhadra_yoga(planet_houses, planet_signs),
        detect_shasha_yoga(planet_houses, planet_signs),
        detect_saraswati_yoga(planet_houses, planet_signs),
        detect_lakshmi_yoga(planet_houses, planet_signs, lagna),
        detect_chandra_adhi_yoga(planet_houses),
        detect_vesi_yoga(planet_houses),
        detect_vasi_yoga(planet_houses),
        detect_ubhayachari_yoga(planet_houses),
        detect_sunapha_yoga(planet_houses),
        detect_anapha_yoga(planet_houses),
        detect_durudhara_yoga(planet_houses),
        detect_kemdrum_yoga(planet_houses),
        detect_kemdrum_bhanga(planet_houses, planet_signs),
        detect_amala_yoga(planet_houses),
        detect_shakata_yoga(planet_houses),
        detect_guru_mangal_yoga(planet_houses),
        detect_parivartana_yoga(planet_houses, planet_signs, lagna),
    ]
