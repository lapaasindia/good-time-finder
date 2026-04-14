"""Unit tests for muhurtha rules using a mocked AstroContext."""

from datetime import datetime, timezone

import pytest

from app.core.enums import ZODIAC_SIGNS
from app.core.models import AstroContext, GeoLocation, Person
from app.rules.travel import (
    BadConstellationForTravelRule,
    BadLunarDayForTravelRule,
    BadWeekdayForTravelRule,
    GoodConstellationForTravelRule,
    GoodLagnaForTravelRule,
    GoodLunarDayForTravelRule,
    GoodWeekdayForTravelRule,
)
from app.rules.marriage import (
    GoodLunarDayForMarriageRule,
    GoodNakshatraForMarriageRule,
    GoodWeekdayForMarriageRule,
)
from app.rules.general import (
    BadMoonSignRule,
    GoodMoonSignRule,
    JupiterInGoodHouseRule,
    SaturnInBadHouseRule,
)

_DT = datetime(2026, 4, 12, 10, 0, tzinfo=timezone.utc)
_LOC = GeoLocation(latitude=28.6, longitude=77.2, timezone="Asia/Kolkata")
_PERSON = Person(
    name="Test",
    birth_datetime=_DT,
    birth_location=_LOC,
)


def _ctx(
    lunar_day: int = 5,
    moon_constellation: str = "Ashwini",
    nakshatra_pada: int = 1,
    weekday: str = "Wednesday",
    lagna: str = "Aries",
    moon_sign: str = "Taurus",
    sun_sign: str = "Aries",
    planet_houses: dict | None = None,
) -> AstroContext:
    return AstroContext(
        dt=_DT,
        location=_LOC,
        lunar_day=lunar_day,
        moon_constellation=moon_constellation,
        nakshatra_pada=nakshatra_pada,
        weekday=weekday,
        lagna=lagna,
        moon_sign=moon_sign,
        sun_sign=sun_sign,
        planet_houses=planet_houses or {"Jupiter": 5, "Saturn": 3},
    )


# ──────────────────────────────────────────
# Travel rules
# ──────────────────────────────────────────


class TestGoodLunarDayForTravel:
    def test_good_tithi_occurs(self):
        for tithi in [2, 3, 5, 7, 10, 11, 13]:
            result = GoodLunarDayForTravelRule().evaluate(_ctx(lunar_day=tithi), _PERSON)
            assert result.occurring, f"Expected occurring for tithi {tithi}"

    def test_bad_tithi_not_occurring(self):
        result = GoodLunarDayForTravelRule().evaluate(_ctx(lunar_day=1), _PERSON)
        assert not result.occurring

    def test_details_populated(self):
        result = GoodLunarDayForTravelRule().evaluate(_ctx(lunar_day=5), _PERSON)
        assert result.details["lunar_day"] == 5


class TestBadLunarDayForTravel:
    def test_bad_tithi_occurs(self):
        for tithi in [1, 8, 9, 14, 15]:
            result = BadLunarDayForTravelRule().evaluate(_ctx(lunar_day=tithi), _PERSON)
            assert result.occurring, f"Expected occurring for tithi {tithi}"

    def test_good_tithi_not_occurring(self):
        result = BadLunarDayForTravelRule().evaluate(_ctx(lunar_day=5), _PERSON)
        assert not result.occurring


class TestConstellationForTravel:
    def test_good_nakshatra(self):
        result = GoodConstellationForTravelRule().evaluate(
            _ctx(moon_constellation="Ashwini"), _PERSON
        )
        assert result.occurring

    def test_bad_nakshatra(self):
        result = BadConstellationForTravelRule().evaluate(
            _ctx(moon_constellation="Bharani"), _PERSON
        )
        assert result.occurring

    def test_neutral_nakshatra_not_good(self):
        result = GoodConstellationForTravelRule().evaluate(
            _ctx(moon_constellation="Bharani"), _PERSON
        )
        assert not result.occurring


class TestLagnaForTravel:
    def test_good_lagna_occurs(self):
        for sign in ["Aries", "Taurus", "Cancer", "Leo", "Libra", "Sagittarius"]:
            result = GoodLagnaForTravelRule().evaluate(_ctx(lagna=sign), _PERSON)
            assert result.occurring, f"Expected occurring for lagna {sign}"

    def test_bad_lagna_not_occurring(self):
        result = GoodLagnaForTravelRule().evaluate(_ctx(lagna="Scorpio"), _PERSON)
        assert not result.occurring


class TestWeekdayForTravel:
    def test_good_weekday(self):
        for day in ["Wednesday", "Thursday", "Friday"]:
            result = GoodWeekdayForTravelRule().evaluate(_ctx(weekday=day), _PERSON)
            assert result.occurring

    def test_bad_weekday(self):
        for day in ["Saturday", "Tuesday"]:
            result = BadWeekdayForTravelRule().evaluate(_ctx(weekday=day), _PERSON)
            assert result.occurring

    def test_good_not_bad(self):
        result = BadWeekdayForTravelRule().evaluate(_ctx(weekday="Wednesday"), _PERSON)
        assert not result.occurring


# ──────────────────────────────────────────
# Marriage rules
# ──────────────────────────────────────────


class TestMarriageRules:
    def test_good_lunar_day(self):
        result = GoodLunarDayForMarriageRule().evaluate(_ctx(lunar_day=5), _PERSON)
        assert result.occurring

    def test_good_nakshatra(self):
        result = GoodNakshatraForMarriageRule().evaluate(
            _ctx(moon_constellation="Rohini"), _PERSON
        )
        assert result.occurring

    def test_good_weekday(self):
        result = GoodWeekdayForMarriageRule().evaluate(_ctx(weekday="Monday"), _PERSON)
        assert result.occurring


# ──────────────────────────────────────────
# General rules
# ──────────────────────────────────────────


class TestGeneralRules:
    def test_good_moon_sign(self):
        result = GoodMoonSignRule().evaluate(_ctx(moon_sign="Taurus"), _PERSON)
        assert result.occurring

    def test_bad_moon_sign(self):
        result = BadMoonSignRule().evaluate(_ctx(moon_sign="Scorpio"), _PERSON)
        assert result.occurring

    def test_jupiter_good_house(self):
        result = JupiterInGoodHouseRule().evaluate(
            _ctx(planet_houses={"Jupiter": 5, "Saturn": 2}), _PERSON
        )
        assert result.occurring

    def test_saturn_bad_house(self):
        result = SaturnInBadHouseRule().evaluate(
            _ctx(planet_houses={"Jupiter": 3, "Saturn": 8}), _PERSON
        )
        assert result.occurring
