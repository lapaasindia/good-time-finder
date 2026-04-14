"""
Muhurtha rules for Travel.
Sources: BV Raman - Muhurtha, classical texts.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {2, 3, 5, 7, 10, 11, 13}
_BAD_LUNAR_DAYS = {1, 14, 15, 8, 9}

_GOOD_CONSTELLATIONS = {
    "Ashwini", "Mrigashira", "Punarvasu", "Pushya",
    "Hasta", "Anuradha", "Shravana", "Dhanishta", "Revati",
}
_BAD_CONSTELLATIONS = {
    "Bharani", "Krittika", "Ardra", "Ashlesha",
    "Magha", "Jyeshtha", "Mula", "Purva Ashadha",
}

_GOOD_LAGNA = {
    "Aries", "Taurus", "Cancer", "Leo", "Libra", "Sagittarius",
}

_GOOD_WEEKDAYS = {"Wednesday", "Thursday", "Friday"}
_BAD_WEEKDAYS = {"Saturday", "Tuesday"}


class GoodLunarDayForTravelRule(MuhurthaRule):
    key = "good_lunar_day_for_travel"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
            details={"lunar_day": ctx.lunar_day},
        )


class BadLunarDayForTravelRule(MuhurthaRule):
    key = "bad_lunar_day_for_travel"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.lunar_day in _BAD_LUNAR_DAYS,
            details={"lunar_day": ctx.lunar_day},
        )


class GoodConstellationForTravelRule(MuhurthaRule):
    key = "good_constellation_for_travel"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.moon_constellation in _GOOD_CONSTELLATIONS,
            details={"nakshatra": ctx.moon_constellation},
        )


class BadConstellationForTravelRule(MuhurthaRule):
    key = "bad_constellation_for_travel"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.moon_constellation in _BAD_CONSTELLATIONS,
            details={"nakshatra": ctx.moon_constellation},
        )


class GoodLagnaForTravelRule(MuhurthaRule):
    key = "good_lagna_for_travel"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.lagna in _GOOD_LAGNA,
            details={"lagna": ctx.lagna},
        )


class BestLagnaForTravelRule(MuhurthaRule):
    """Lagna matches natal moon sign — most personalised indicator."""

    key = "best_lagna_for_travel"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        from app.astrology.calculations import natal_moon_sign
        natal_moon = natal_moon_sign(person)
        return RuleResult(
            occurring=ctx.lagna == natal_moon,
            details={"lagna": ctx.lagna, "natal_moon": natal_moon},
        )


class GoodWeekdayForTravelRule(MuhurthaRule):
    key = "good_weekday_for_travel"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.weekday in _GOOD_WEEKDAYS,
            details={"weekday": ctx.weekday},
        )


class BadWeekdayForTravelRule(MuhurthaRule):
    key = "bad_weekday_for_travel"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.weekday in _BAD_WEEKDAYS,
            details={"weekday": ctx.weekday},
        )
