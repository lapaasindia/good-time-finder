"""
Muhurtha rules for Finance — investments, loans, wealth activities.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {2, 3, 5, 7, 10, 11, 13}
_BAD_LUNAR_DAYS = {4, 8, 9, 14, 15}
_GOOD_WEEKDAYS = {"Wednesday", "Thursday", "Friday"}
_BAD_WEEKDAYS = {"Saturday", "Tuesday"}
_GOOD_NAKSHATRAS = {
    "Rohini", "Mrigashira", "Pushya", "Uttara Phalguni",
    "Hasta", "Anuradha", "Shravana", "Revati",
}
_BAD_NAKSHATRAS = {"Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula"}
_GOOD_LAGNA = {"Taurus", "Cancer", "Virgo", "Libra", "Sagittarius", "Pisces"}


class GoodLunarDayForFinanceRule(MuhurthaRule):
    key = "good_lunar_day_for_finance"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class BadLunarDayForFinanceRule(MuhurthaRule):
    key = "bad_lunar_day_for_finance"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _BAD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class GoodWeekdayForFinanceRule(MuhurthaRule):
    key = "good_weekday_for_finance"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodNakshatraForFinanceRule(MuhurthaRule):
    key = "good_nakshatra_for_finance"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class GoodLagnaForFinanceRule(MuhurthaRule):
    key = "good_lagna_for_finance"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lagna in _GOOD_LAGNA,
                          details={"lagna": ctx.lagna})


class JupiterInWealthHouseRule(MuhurthaRule):
    """Jupiter in 2nd, 5th, 9th, or 11th house favours wealth."""

    key = "jupiter_in_wealth_house"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Jupiter")
        return RuleResult(occurring=house in {2, 5, 9, 11},
                          details={"jupiter_house": house})


class VenusInGoodHouseForFinanceRule(MuhurthaRule):
    key = "venus_in_good_house_finance"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Venus")
        return RuleResult(occurring=house in {1, 2, 5, 9, 11},
                          details={"venus_house": house})
