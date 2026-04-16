"""
Special natal chart conditions.

Covers:
- Kaal Sarp Dosha  — all 7 planets between Rahu & Ketu axis
- Mangal Dosha     — Mars in 1st/2nd/4th/7th/8th/12th from lagna/moon/venus
- Combustion       — planet too close to Sun (loses strength)
- Retrograde       — planet moving backward (intensified/internal energy)
- Graha Yuddha     — planetary war (two planets within 1° of each other)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
import os

import swisseph as swe

# Configure Swiss Ephemeris path to use bundled or system ephemeris files
_ephem_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ephemeris")
if os.path.exists(_ephem_path):
    swe.set_ephe_path(_ephem_path)
else:
    # Fallback to system paths
    swe.set_ephe_path("/usr/share/swisseph")

from app.core.enums import ZODIAC_SIGNS

COMBUSTION_ORBS: dict[str, float] = {
    "Moon":    12.0,
    "Mars":     17.0,
    "Mercury":  14.0,
    "Jupiter":  11.0,
    "Venus":    10.0,
    "Saturn":   15.0,
}

RETROGRADE_PLANETS = {"Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}

MANGAL_DOSHA_HOUSES = {1, 2, 4, 7, 8, 12}


@dataclass
class CombustionResult:
    planet: str
    combust: bool
    orb_degrees: float
    strength_penalty: float


@dataclass
class RetrogradeResult:
    planet: str
    retrograde: bool
    strength_modifier: float


@dataclass
class GrahaYuddhaResult:
    winner: str
    loser: str
    orb: float
    loser_strength_penalty: float


@dataclass
class DoshaDetail:
    name: str
    present: bool
    severity: str
    description: str
    effects: str
    remedies: list[str]
    penalty: float


@dataclass
class SpecialConditions:
    kaal_sarp_dosha: bool
    kaal_sarp_type: str
    mangal_dosha: bool
    mangal_dosha_positions: list[str]
    pitru_dosha: bool
    guru_chandal_dosha: bool
    shrapit_dosha: bool
    grahan_dosha: bool
    grahan_dosha_planets: list[str]
    daridra_dosha: bool
    combustion: dict[str, CombustionResult]
    retrograde: dict[str, RetrogradeResult]
    graha_yuddha: list[GrahaYuddhaResult]
    overall_penalty: float

    def dosha_details(self) -> list[dict]:
        """Return rich detail for every dosha — present or not."""
        details: list[DoshaDetail] = []

        details.append(DoshaDetail(
            name="Kaal Sarp Dosha",
            present=self.kaal_sarp_dosha,
            severity="high" if self.kaal_sarp_dosha else "none",
            description=(
                f"All seven planets hemmed between Rahu–Ketu axis ({self.kaal_sarp_type}). "
                "Per BPHS, this amplifies karmic intensity across all life areas, "
                "causing sudden ups and downs, obstacles in career, and delays."
            ) if self.kaal_sarp_dosha else (
                "All planets are NOT confined between the Rahu–Ketu axis. "
                "Kaal Sarp Dosha is absent — no karmic amplification from this combination."
            ),
            effects="Sudden reversals, obstacles, delays, intense karmic lessons, "
                    "fear of serpents/hidden enemies." if self.kaal_sarp_dosha else "",
            remedies=[
                "Kaal Sarp Puja at Trimbakeshwar or Srikalahasti temple",
                "Recite Rahu Mantra (Om Bhram Bhreem Bhroum Sah Rahave Namah) 18,000 times",
                "Donate black sesame seeds on Saturday",
                "Worship Lord Shiva with Rudrabhishekam",
                "Wear Gomed (Hessonite) gemstone after consulting astrologer",
            ] if self.kaal_sarp_dosha else [],
            penalty=-1.5 if self.kaal_sarp_dosha else 0.0,
        ))

        details.append(DoshaDetail(
            name="Mangal Dosha",
            present=self.mangal_dosha,
            severity="high" if len(self.mangal_dosha_positions) >= 2 else (
                "moderate" if self.mangal_dosha else "none"),
            description=(
                "Mars occupies houses 1/2/4/7/8/12 from Lagna, Moon, or Venus. "
                "Positions: " + "; ".join(self.mangal_dosha_positions) + ". "
                "Per classical texts, Mars in these houses creates aggression, "
                "conflicts, and challenges in marital life."
            ) if self.mangal_dosha else (
                "Mars is NOT in houses 1/2/4/7/8/12 from Lagna, Moon, or Venus. "
                "Mangal Dosha is absent — no adverse Mars influence on marriage/partnerships."
            ),
            effects="Marital discord, delayed marriage, partner health issues, "
                    "aggression in relationships." if self.mangal_dosha else "",
            remedies=[
                "Kumbh Vivah (symbolic marriage to a pot/tree before actual marriage)",
                "Recite Mangal Mantra (Om Kraam Kreem Kroum Sah Bhaumaya Namah)",
                "Fast on Tuesdays and donate red lentils",
                "Worship Lord Hanuman on Tuesdays",
                "Wear Red Coral (Moonga) after astrological consultation",
            ] if self.mangal_dosha else [],
            penalty=-1.0 if self.mangal_dosha else 0.0,
        ))

        details.append(DoshaDetail(
            name="Pitru Dosha",
            present=self.pitru_dosha,
            severity="high" if self.pitru_dosha else "none",
            description=(
                "Sun conjunct Rahu or Ketu (within same house) — indicates "
                "ancestral karmic debt. Per Lal Kitab and BPHS, the native "
                "carries unresolved karmas from paternal lineage, affecting "
                "career, self-confidence, and father's health."
            ) if self.pitru_dosha else (
                "Sun is free from Rahu/Ketu conjunction. "
                "No ancestral karmic debt indicated — Pitru Dosha is absent."
            ),
            effects="Obstacles in career, strained father relationship, "
                    "difficulty in getting blessings from elders, recurring "
                    "family problems." if self.pitru_dosha else "",
            remedies=[
                "Perform Pitru Tarpan on Amavasya (new moon) days",
                "Offer water to the Sun every morning (Surya Arghya)",
                "Donate food to Brahmins on father's or grandfather's death anniversary",
                "Recite Surya Mantra and Rahu Mantra regularly",
                "Perform Narayan Nagbali Puja at Trimbakeshwar",
            ] if self.pitru_dosha else [],
            penalty=-1.0 if self.pitru_dosha else 0.0,
        ))

        details.append(DoshaDetail(
            name="Guru Chandal Dosha",
            present=self.guru_chandal_dosha,
            severity="moderate" if self.guru_chandal_dosha else "none",
            description=(
                "Jupiter conjunct Rahu or Ketu — the Guru (divine teacher) is "
                "afflicted by shadow planets. Per BPHS, this corrupts Jupiter's "
                "significations: wisdom, dharma, children, and expansion become "
                "tainted with confusion, unethical shortcuts, or spiritual deception."
            ) if self.guru_chandal_dosha else (
                "Jupiter is free from Rahu/Ketu conjunction. "
                "Guru Chandal Dosha is absent — Jupiter's wisdom flows unobstructed."
            ),
            effects="Wrong spiritual guidance, financial losses through bad advice, "
                    "children-related concerns, ethical dilemmas." if self.guru_chandal_dosha else "",
            remedies=[
                "Worship Lord Vishnu on Thursdays",
                "Recite Guru Mantra (Om Graam Greem Groum Sah Gurave Namah)",
                "Donate yellow items (turmeric, yellow cloth, gold) on Thursdays",
                "Feed cows with jaggery and gram on Thursdays",
                "Wear Yellow Sapphire (Pukhraj) after consultation",
            ] if self.guru_chandal_dosha else [],
            penalty=-0.8 if self.guru_chandal_dosha else 0.0,
        ))

        details.append(DoshaDetail(
            name="Shrapit Dosha",
            present=self.shrapit_dosha,
            severity="high" if self.shrapit_dosha else "none",
            description=(
                "Saturn conjunct Rahu in the natal chart — the 'Cursed' yoga. "
                "Per Lal Kitab, this is one of the most severe karmic indicators, "
                "suggesting a curse from a past life carried forward. It creates "
                "persistent obstacles, delays, and suffering across life areas."
            ) if self.shrapit_dosha else (
                "Saturn and Rahu are NOT conjunct. "
                "Shrapit Dosha is absent — no past-life curse influence."
            ),
            effects="Chronic delays, persistent bad luck, health issues, "
                    "broken relationships, professional stagnation." if self.shrapit_dosha else "",
            remedies=[
                "Perform Shrapit Dosha Nivaran Puja",
                "Recite Maha Mrityunjaya Mantra 1.25 lakh times",
                "Donate black items (mustard oil, black cloth) on Saturdays",
                "Feed crows and stray dogs regularly",
                "Visit Shani temple on Saturdays and light sesame oil lamp",
            ] if self.shrapit_dosha else [],
            penalty=-1.5 if self.shrapit_dosha else 0.0,
        ))

        details.append(DoshaDetail(
            name="Grahan Dosha",
            present=self.grahan_dosha,
            severity="moderate" if self.grahan_dosha else "none",
            description=(
                "Sun or Moon conjunct Rahu or Ketu (eclipse yoga). "
                "Affected luminaries: " + ", ".join(self.grahan_dosha_planets) + ". "
                "Per classical Jyotish, this weakens the luminary's significations — "
                "Sun (father, authority, health) or Moon (mind, mother, emotions)."
            ) if self.grahan_dosha else (
                "Sun and Moon are free from Rahu/Ketu conjunction. "
                "Grahan Dosha is absent — luminaries are uneclipsed."
            ),
            effects="Mental anxiety, health fluctuations, authority challenges, "
                    "mother/father health concerns." if self.grahan_dosha else "",
            remedies=[
                "Perform Grahan Dosha Shanti Puja",
                "Chant Chandra Mantra or Surya Mantra (depending on affected luminary)",
                "Donate white items on Monday (Moon) or wheat on Sunday (Sun)",
                "Observe fasting during actual lunar/solar eclipses",
                "Wear Pearl (Moon) or Ruby (Sun) after consulting astrologer",
            ] if self.grahan_dosha else [],
            penalty=-0.7 if self.grahan_dosha else 0.0,
        ))

        details.append(DoshaDetail(
            name="Daridra Dosha",
            present=self.daridra_dosha,
            severity="moderate" if self.daridra_dosha else "none",
            description=(
                "Lord of 11th house (gains) is placed in a Dusthana (6th/8th/12th). "
                "Per BPHS, this weakens the house of income, causing financial "
                "struggles, blocked gains, and difficulty accumulating wealth."
            ) if self.daridra_dosha else (
                "Lord of the 11th house is NOT in a Dusthana. "
                "Daridra Dosha is absent — income channels are unobstructed."
            ),
            effects="Financial hardship, blocked income, debts, inability to "
                    "save money, dependence on others." if self.daridra_dosha else "",
            remedies=[
                "Recite Lakshmi Mantra (Om Shreem Mahalakshmiyei Namah) daily",
                "Donate food and clothes to the needy on Fridays",
                "Worship Lord Vishnu and Goddess Lakshmi on Thursdays and Fridays",
                "Keep the North direction of home clean and clutter-free",
                "Light a ghee lamp at home every evening",
            ] if self.daridra_dosha else [],
            penalty=-0.8 if self.daridra_dosha else 0.0,
        ))

        return [
            {
                "name": d.name,
                "present": d.present,
                "severity": d.severity,
                "description": d.description,
                "effects": d.effects,
                "remedies": d.remedies,
                "penalty": d.penalty,
            }
            for d in details
        ]

    def summary(self) -> dict:
        return {
            "kaal_sarp_dosha": self.kaal_sarp_dosha,
            "kaal_sarp_type": self.kaal_sarp_type,
            "mangal_dosha": self.mangal_dosha,
            "mangal_dosha_positions": self.mangal_dosha_positions,
            "pitru_dosha": self.pitru_dosha,
            "guru_chandal_dosha": self.guru_chandal_dosha,
            "shrapit_dosha": self.shrapit_dosha,
            "grahan_dosha": self.grahan_dosha,
            "grahan_dosha_planets": self.grahan_dosha_planets,
            "daridra_dosha": self.daridra_dosha,
            "combust_planets": [p for p, r in self.combustion.items() if r.combust],
            "retrograde_planets": [p for p, r in self.retrograde.items() if r.retrograde],
            "graha_yuddha": [
                {"winner": g.winner, "loser": g.loser, "orb": g.orb}
                for g in self.graha_yuddha
            ],
            "dosha_details": self.dosha_details(),
            "overall_penalty": self.overall_penalty,
        }


def get_raw_longitudes(dt: datetime) -> dict[str, float]:
    """Public alias for raw sidereal longitudes."""
    return _get_raw_longitudes(dt)


def get_speeds(dt: datetime) -> dict[str, float]:
    """Public alias for planetary speeds (negative = retrograde)."""
    return _get_speeds(dt)


_PLANET_IDS_LONGS = None

def _ensure_planet_ids_longs():
    global _PLANET_IDS_LONGS
    if _PLANET_IDS_LONGS is None:
        _PLANET_IDS_LONGS = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
            "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS, "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE,
        }
    return _PLANET_IDS_LONGS


def _dt_to_jd(dt: datetime) -> float:
    utc = dt.astimezone(timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute / 60.0 + utc.second / 3600.0)


@lru_cache(maxsize=4096)
def _get_raw_longitudes_cached(jd: float) -> tuple:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    planet_ids = _ensure_planet_ids_longs()
    longitudes: dict[str, float] = {}
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    for name, pid in planet_ids.items():
        result, _ = swe.calc_ut(jd, pid, flags)
        longitudes[name] = result[0] % 360
    longitudes["Ketu"] = (longitudes["Rahu"] + 180) % 360
    return tuple(sorted(longitudes.items()))


def _get_raw_longitudes(dt: datetime) -> dict[str, float]:
    jd = _dt_to_jd(dt)
    return dict(_get_raw_longitudes_cached(jd))


_PLANET_IDS_SPEEDS = None

def _ensure_planet_ids_speeds():
    global _PLANET_IDS_SPEEDS
    if _PLANET_IDS_SPEEDS is None:
        _PLANET_IDS_SPEEDS = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
            "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS, "Saturn": swe.SATURN,
        }
    return _PLANET_IDS_SPEEDS


@lru_cache(maxsize=4096)
def _get_speeds_cached(jd: float) -> tuple:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    planet_ids = _ensure_planet_ids_speeds()
    speeds: dict[str, float] = {}
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    for name, pid in planet_ids.items():
        result, _ = swe.calc_ut(jd, pid, flags)
        speeds[name] = result[3]
    return tuple(sorted(speeds.items()))


def _get_speeds(dt: datetime) -> dict[str, float]:
    jd = _dt_to_jd(dt)
    return dict(_get_speeds_cached(jd))


def _angular_diff(lon1: float, lon2: float) -> float:
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def detect_kaal_sarp(longitudes: dict[str, float]) -> tuple[bool, str]:
    rahu_lon = longitudes["Rahu"]
    ketu_lon = longitudes["Ketu"]

    other_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    def _in_rahu_ketu_arc(lon: float) -> bool:
        arc_start = rahu_lon
        arc_end = ketu_lon
        span = (arc_end - arc_start) % 360
        pos = (lon - arc_start) % 360
        return pos <= span

    all_in = all(_in_rahu_ketu_arc(longitudes[p]) for p in other_planets)
    all_out = all(not _in_rahu_ketu_arc(longitudes[p]) for p in other_planets)
    present = all_in or all_out

    if not present:
        return False, ""

    rahu_sign = ZODIAC_SIGNS[int(rahu_lon / 30) % 12]
    ketu_sign = ZODIAC_SIGNS[int(ketu_lon / 30) % 12]
    ksd_type = f"{rahu_sign}-{ketu_sign} Kaal Sarp"
    return True, ksd_type


def detect_mangal_dosha(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
    lagna_sign: str,
) -> tuple[bool, list[str]]:
    mars_house = planet_houses.get("Mars", 0)
    moon_house = planet_houses.get("Moon", 0)
    venus_house = planet_houses.get("Venus", 0)

    positions = []

    if mars_house in MANGAL_DOSHA_HOUSES:
        positions.append(f"Mars in house {mars_house} from Lagna")

    moon_rel = ((mars_house - moon_house) % 12) + 1
    if moon_rel in MANGAL_DOSHA_HOUSES:
        positions.append(f"Mars in house {moon_rel} from Moon")

    venus_rel = ((mars_house - venus_house) % 12) + 1
    if venus_rel in MANGAL_DOSHA_HOUSES:
        positions.append(f"Mars in house {venus_rel} from Venus")

    return bool(positions), positions


def detect_combustion(longitudes: dict[str, float]) -> dict[str, CombustionResult]:
    sun_lon = longitudes["Sun"]
    results: dict[str, CombustionResult] = {}
    for planet, max_orb in COMBUSTION_ORBS.items():
        if planet not in longitudes:
            continue
        orb = _angular_diff(longitudes[planet], sun_lon)
        combust = orb <= max_orb
        penalty = -round((1.0 - orb / max_orb) * 0.6, 3) if combust else 0.0
        results[planet] = CombustionResult(
            planet=planet,
            combust=combust,
            orb_degrees=round(orb, 2),
            strength_penalty=penalty,
        )
    return results


def detect_retrograde(speeds: dict[str, float]) -> dict[str, RetrogradeResult]:
    results: dict[str, RetrogradeResult] = {}
    for planet, speed in speeds.items():
        retro = speed < 0
        modifier = 1.15 if retro else 1.0
        results[planet] = RetrogradeResult(
            planet=planet,
            retrograde=retro,
            strength_modifier=modifier,
        )
    return results


def detect_graha_yuddha(longitudes: dict[str, float]) -> list[GrahaYuddhaResult]:
    planets = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    results: list[GrahaYuddhaResult] = []
    for i, p1 in enumerate(planets):
        for p2 in planets[i + 1:]:
            if p1 not in longitudes or p2 not in longitudes:
                continue
            orb = _angular_diff(longitudes[p1], longitudes[p2])
            if orb <= 1.0:
                winner = p1 if longitudes[p1] < longitudes[p2] else p2
                loser = p2 if winner == p1 else p1
                results.append(GrahaYuddhaResult(
                    winner=winner,
                    loser=loser,
                    orb=round(orb, 3),
                    loser_strength_penalty=-0.4,
                ))
    return results


SIGN_LORD: dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}


def detect_pitru_dosha(planet_houses: dict[str, int]) -> bool:
    """Sun conjunct Rahu or Ketu in same house."""
    sun_h = planet_houses.get("Sun", 0)
    rahu_h = planet_houses.get("Rahu", -1)
    ketu_h = planet_houses.get("Ketu", -2)
    return sun_h == rahu_h or sun_h == ketu_h


def detect_guru_chandal_dosha(planet_houses: dict[str, int]) -> bool:
    """Jupiter conjunct Rahu or Ketu in same house."""
    jup_h = planet_houses.get("Jupiter", 0)
    rahu_h = planet_houses.get("Rahu", -1)
    ketu_h = planet_houses.get("Ketu", -2)
    return jup_h == rahu_h or jup_h == ketu_h


def detect_shrapit_dosha(planet_houses: dict[str, int]) -> bool:
    """Saturn conjunct Rahu in same house."""
    sat_h = planet_houses.get("Saturn", 0)
    rahu_h = planet_houses.get("Rahu", -1)
    return sat_h == rahu_h


def detect_grahan_dosha(planet_houses: dict[str, int]) -> tuple[bool, list[str]]:
    """Sun or Moon conjunct Rahu or Ketu (eclipse combination)."""
    rahu_h = planet_houses.get("Rahu", -1)
    ketu_h = planet_houses.get("Ketu", -2)
    affected: list[str] = []
    for luminary in ["Sun", "Moon"]:
        lum_h = planet_houses.get(luminary, 0)
        if lum_h == rahu_h or lum_h == ketu_h:
            affected.append(luminary)
    return bool(affected), affected


def detect_daridra_dosha(
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
    lagna_sign: str,
) -> bool:
    """Lord of 11th house placed in 6th, 8th, or 12th house."""
    lagna_idx = ZODIAC_SIGNS.index(lagna_sign)
    eleventh_sign = ZODIAC_SIGNS[(lagna_idx + 10) % 12]
    lord_of_11 = SIGN_LORD.get(eleventh_sign, "")
    if not lord_of_11:
        return False
    lord_house = planet_houses.get(lord_of_11, 0)
    return lord_house in {6, 8, 12}


def compute_special_conditions(
    dt: datetime,
    planet_houses: dict[str, int],
    planet_signs: dict[str, str],
    lagna_sign: str,
) -> SpecialConditions:
    longitudes = _get_raw_longitudes(dt)
    speeds = _get_speeds(dt)

    ksd, ksd_type = detect_kaal_sarp(longitudes)
    mangal, mangal_pos = detect_mangal_dosha(planet_houses, planet_signs, lagna_sign)
    pitru = detect_pitru_dosha(planet_houses)
    guru_chandal = detect_guru_chandal_dosha(planet_houses)
    shrapit = detect_shrapit_dosha(planet_houses)
    grahan, grahan_planets = detect_grahan_dosha(planet_houses)
    daridra = detect_daridra_dosha(planet_houses, planet_signs, lagna_sign)
    combustion = detect_combustion(longitudes)
    retrograde = detect_retrograde(speeds)
    yuddha = detect_graha_yuddha(longitudes)

    penalty = 0.0
    if ksd:
        penalty -= 1.5
    if mangal:
        penalty -= 1.0
    if pitru:
        penalty -= 1.0
    if guru_chandal:
        penalty -= 0.8
    if shrapit:
        penalty -= 1.5
    if grahan:
        penalty -= 0.7
    if daridra:
        penalty -= 0.8
    penalty += sum(r.strength_penalty for r in combustion.values())
    penalty += sum(g.loser_strength_penalty for g in yuddha)

    return SpecialConditions(
        kaal_sarp_dosha=ksd,
        kaal_sarp_type=ksd_type,
        mangal_dosha=mangal,
        mangal_dosha_positions=mangal_pos,
        pitru_dosha=pitru,
        guru_chandal_dosha=guru_chandal,
        shrapit_dosha=shrapit,
        grahan_dosha=grahan,
        grahan_dosha_planets=grahan_planets,
        daridra_dosha=daridra,
        combustion=combustion,
        retrograde=retrograde,
        graha_yuddha=yuddha,
        overall_penalty=round(penalty, 3),
    )


def apply_combustion_to_shadbala(
    shadbala: dict[str, float],
    combustion: dict[str, CombustionResult],
    retrograde: dict[str, RetrogradeResult],
) -> dict[str, float]:
    adjusted = dict(shadbala)
    for planet, res in combustion.items():
        if res.combust and planet in adjusted:
            adjusted[planet] = max(0.0, round(adjusted[planet] + res.strength_penalty, 3))
    for planet, res in retrograde.items():
        if res.retrograde and planet in adjusted:
            adjusted[planet] = round(adjusted[planet] * res.strength_modifier, 3)
    return adjusted
