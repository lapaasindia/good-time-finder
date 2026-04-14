"""
Panchang — Five Limbs of Vedic Time.

The Panchang is the five-fold calendar used in muhurtha:
  1. Vara      — weekday (already in calculations.py)
  2. Tithi     — lunar day (already computed as lunar_day)
  3. Nakshatra — Moon's asterism (already computed)
  4. Yoga      — 27 yogas based on Sun + Moon longitude sum
  5. Karana    — 11 karanas (half-tithi)

This module adds Yoga and Karana which were missing.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import swisseph as swe

YOGA_NAMES = [
    "Vishkamba", "Preeti",   "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda",  "Sukarma",  "Dhriti",   "Shula",     "Ganda",
    "Vriddhi",   "Dhruva",   "Vyaghata", "Harshana",  "Vajra",
    "Siddhi",    "Vyatipata","Variyan",  "Parigha",   "Shiva",
    "Siddha",    "Sadhya",   "Shubha",   "Shukla",    "Brahma",
    "Indra",     "Vaidhriti",
]

YOGA_NATURE: dict[str, str] = {
    "Preeti":    "good", "Ayushman":  "good", "Saubhagya": "good",
    "Shobhana":  "good", "Sukarma":   "good", "Dhriti":    "good",
    "Harshana":  "good", "Siddhi":    "good", "Variyan":   "good",
    "Shiva":     "good", "Siddha":    "good", "Sadhya":    "good",
    "Shubha":    "good", "Shukla":    "good", "Brahma":    "good",
    "Indra":     "good", "Vriddhi":   "good", "Dhruva":    "good",
    "Vishkamba": "bad",  "Atiganda":  "bad",  "Shula":     "bad",
    "Ganda":     "bad",  "Vyaghata":  "bad",  "Vajra":     "bad",
    "Vyatipata": "bad",  "Parigha":   "bad",  "Vaidhriti": "bad",
}

KARANA_NAMES_REPEATING = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]
KARANA_NAMES_FIXED = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]
KARANA_NATURE: dict[str, str] = {
    "Bava":        "good", "Balava":       "good", "Kaulava":      "good",
    "Taitila":     "good", "Garaja":        "good", "Vanija":       "good",
    "Vishti":      "bad",  "Shakuni":       "neutral", "Chatushpada": "neutral",
    "Naga":        "neutral", "Kimstughna": "neutral",
}


@dataclass
class PanchangData:
    tithi: int
    nakshatra: str
    weekday: str
    yoga_name: str
    yoga_nature: str
    karana_name: str
    karana_nature: str
    yoga_score: float
    karana_score: float

    def is_auspicious(self) -> bool:
        return self.yoga_nature == "good" and self.karana_nature != "bad"


def _get_sidereal_longitudes(jd: float) -> tuple[float, float]:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun, _ = swe.calc_ut(jd, swe.SUN, flags)
    moon, _ = swe.calc_ut(jd, swe.MOON, flags)
    return sun[0], moon[0]


def compute_yoga(dt: datetime) -> tuple[str, str]:
    utc = dt.astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute / 60.0 + utc.second / 3600.0)
    sun_lon, moon_lon = _get_sidereal_longitudes(jd)
    total = (sun_lon + moon_lon) % 360
    yoga_index = int(total / (360 / 27)) % 27
    name = YOGA_NAMES[yoga_index]
    return name, YOGA_NATURE.get(name, "neutral")


def compute_karana(dt: datetime) -> tuple[str, str]:
    utc = dt.astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute / 60.0 + utc.second / 3600.0)
    sun_lon, moon_lon = _get_sidereal_longitudes(jd)
    diff = (moon_lon - sun_lon) % 360
    karana_index = int(diff / 6)

    if karana_index == 0:
        name = "Kimstughna"
    elif 1 <= karana_index <= 57:
        name = KARANA_NAMES_REPEATING[(karana_index - 1) % 7]
    elif karana_index == 58:
        name = "Shakuni"
    elif karana_index == 59:
        name = "Chatushpada"
    elif karana_index == 60:
        name = "Naga"
    else:
        name = "Kimstughna"

    return name, KARANA_NATURE.get(name, "neutral")


def build_panchang(dt: datetime, nakshatra: str, tithi: int, weekday: str) -> PanchangData:
    yoga_name, yoga_nature = compute_yoga(dt)
    karana_name, karana_nature = compute_karana(dt)

    yoga_score_map = {"good": 1.0, "bad": -1.0, "neutral": 0.0}
    karana_score_map = {"good": 0.5, "bad": -0.5, "neutral": 0.0}

    return PanchangData(
        tithi=tithi,
        nakshatra=nakshatra,
        weekday=weekday,
        yoga_name=yoga_name,
        yoga_nature=yoga_nature,
        karana_name=karana_name,
        karana_nature=karana_nature,
        yoga_score=yoga_score_map[yoga_nature],
        karana_score=karana_score_map[karana_nature],
    )
