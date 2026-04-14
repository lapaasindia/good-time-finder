"""
Muhurtha rules for Property — buying, selling, renting property.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {2, 3, 5, 7, 10, 11, 13}
_BAD_LUNAR_DAYS = {4, 8, 9, 14, 15}
_GOOD_WEEKDAYS = {"Monday", "Wednesday", "Thursday"}
_BAD_WEEKDAYS = {"Saturday", "Tuesday"}
_GOOD_NAKSHATRAS = {
    "Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
    "Anuradha", "Shravana", "Uttara Bhadrapada", "Revati",
}
_GOOD_LAGNA = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn"}


class GoodLunarDayForPropertyRule(MuhurthaRule):
    key = "good_lunar_day_for_property"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class GoodWeekdayForPropertyRule(MuhurthaRule):
    key = "good_weekday_for_property"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodNakshatraForPropertyRule(MuhurthaRule):
    key = "good_nakshatra_for_property"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class GoodLagnaForPropertyRule(MuhurthaRule):
    key = "good_lagna_for_property"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lagna in _GOOD_LAGNA,
                          details={"lagna": ctx.lagna})


class MarsInGoodHouseForPropertyRule(MuhurthaRule):
    """Mars as karaka of property — in 4th or 10th is favourable."""

    key = "mars_in_good_house_property"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Mars")
        return RuleResult(occurring=house in {4, 10, 11},
                          details={"mars_house": house})


class StrongMoonForPropertyRule(MuhurthaRule):
    """Moon as 4th house karaka — in Kendra is auspicious for property."""

    key = "strong_moon_for_property"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Moon")
        return RuleResult(occurring=house in {1, 4, 7, 10},
                          details={"moon_house": house})
