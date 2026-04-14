"""
Astrology calculations using pyswisseph (Swiss Ephemeris).

All public methods receive a datetime (timezone-aware) and GeoLocation,
and return simple Python types (int, str, float, dict).
"""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache

import swisseph as swe

from app.core.enums import NAKSHATRAS, WEEKDAYS, ZODIAC_SIGNS
from app.core.models import AstroContext, GeoLocation, Person

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}


def _to_julian_day(dt: datetime) -> float:
    utc_dt = dt.astimezone(timezone.utc)
    return swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0,
    )


def _planet_longitude(jd: float, planet_id: int) -> float:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    result, _ = swe.calc_ut(jd, planet_id, flags)
    return result[0]


def _longitude_to_sign(longitude: float) -> str:
    index = int(longitude / 30) % 12
    return ZODIAC_SIGNS[index]


def _longitude_to_nakshatra(longitude: float) -> tuple[str, int]:
    nak_index = int(longitude / (360 / 27)) % 27
    pada = int((longitude % (360 / 27)) / (360 / 108)) + 1
    return NAKSHATRAS[nak_index], pada


def lunar_day(dt: datetime, loc: GeoLocation) -> int:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _to_julian_day(dt)
    sun_lon = _planet_longitude(jd, swe.SUN)
    moon_lon = _planet_longitude(jd, swe.MOON)
    diff = (moon_lon - sun_lon) % 360
    tithi = int(diff / 12) + 1
    return tithi


def moon_constellation(dt: datetime, loc: GeoLocation) -> str:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _to_julian_day(dt)
    moon_lon = _planet_longitude(jd, swe.MOON)
    nakshatra, _ = _longitude_to_nakshatra(moon_lon)
    return nakshatra


def nakshatra_pada(dt: datetime, loc: GeoLocation) -> int:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _to_julian_day(dt)
    moon_lon = _planet_longitude(jd, swe.MOON)
    _, pada = _longitude_to_nakshatra(moon_lon)
    return pada


def weekday(dt: datetime) -> str:
    return WEEKDAYS[dt.weekday()]


def rising_sign(dt: datetime, loc: GeoLocation) -> str:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _to_julian_day(dt)
    houses, ascmc = swe.houses_ex(
        jd,
        loc.latitude,
        loc.longitude,
        b"P",
        swe.FLG_SIDEREAL,
    )
    asc_lon = ascmc[0]
    return _longitude_to_sign(asc_lon)


def moon_sign(dt: datetime, loc: GeoLocation) -> str:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _to_julian_day(dt)
    moon_lon = _planet_longitude(jd, swe.MOON)
    return _longitude_to_sign(moon_lon)


def sun_sign(dt: datetime, loc: GeoLocation) -> str:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _to_julian_day(dt)
    sun_lon = _planet_longitude(jd, swe.SUN)
    return _longitude_to_sign(sun_lon)


def natal_moon_sign(person: Person) -> str:
    return moon_sign(person.birth_datetime, person.birth_location)


def natal_lagna(person: Person) -> str:
    return rising_sign(person.birth_datetime, person.birth_location)


def planet_houses(dt: datetime, loc: GeoLocation) -> dict[str, int]:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _to_julian_day(dt)
    houses, ascmc = swe.houses_ex(
        jd,
        loc.latitude,
        loc.longitude,
        b"P",
        swe.FLG_SIDEREAL,
    )
    asc_lon = ascmc[0]

    result = {}
    for name, planet_id in PLANETS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        calc_result, _ = swe.calc_ut(jd, planet_id, flags)
        p_lon = calc_result[0]
        rel = (p_lon - asc_lon) % 360
        house_num = int(rel / 30) + 1
        result[name] = house_num

    return result


def planet_signs(dt: datetime, loc: GeoLocation) -> dict[str, str]:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _to_julian_day(dt)
    result = {}
    for name, planet_id in PLANETS.items():
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        calc_result, _ = swe.calc_ut(jd, planet_id, flags)
        result[name] = _longitude_to_sign(calc_result[0])
    return result


def build_context(dt: datetime, loc: GeoLocation, person: Person) -> AstroContext:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return AstroContext(
        dt=dt,
        location=loc,
        lunar_day=lunar_day(dt, loc),
        moon_constellation=moon_constellation(dt, loc),
        nakshatra_pada=nakshatra_pada(dt, loc),
        weekday=weekday(dt),
        lagna=rising_sign(dt, loc),
        moon_sign=moon_sign(dt, loc),
        sun_sign=sun_sign(dt, loc),
        planet_houses=planet_houses(dt, loc),
        planet_signs=planet_signs(dt, loc),
    )
