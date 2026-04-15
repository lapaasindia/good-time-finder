"""
Muhurtha rules for Business — entrepreneurship, ventures, partnerships, deals.

Key houses: 1st (self/initiative), 2nd (wealth), 7th (partners), 10th (public image), 11th (gains)
Key planets: Mercury (commerce), Jupiter (expansion), Saturn (discipline), Sun (authority), Mars (drive)
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {1, 2, 3, 5, 7, 10, 11, 13}
_BAD_LUNAR_DAYS = {4, 8, 9, 14, 15}

_GOOD_NAKSHATRAS = {
    "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Revati",
}
_BAD_NAKSHATRAS = {"Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula"}

_GOOD_WEEKDAYS = {"Monday", "Wednesday", "Thursday", "Friday"}
_BAD_WEEKDAYS = {"Saturday", "Tuesday"}

_GOOD_LAGNA = {"Taurus", "Gemini", "Leo", "Virgo", "Libra", "Sagittarius", "Capricorn"}


class GoodLunarDayForBusinessRule(MuhurthaRule):
    key = "good_lunar_day_for_business"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class BadLunarDayForBusinessRule(MuhurthaRule):
    key = "bad_lunar_day_for_business"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _BAD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class GoodNakshatraForBusinessRule(MuhurthaRule):
    key = "good_nakshatra_for_business"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class BadNakshatraForBusinessRule(MuhurthaRule):
    key = "bad_nakshatra_for_business"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _BAD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class GoodWeekdayForBusinessRule(MuhurthaRule):
    key = "good_weekday_for_business"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class BadWeekdayForBusinessRule(MuhurthaRule):
    key = "bad_weekday_for_business"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _BAD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodLagnaForBusinessRule(MuhurthaRule):
    key = "good_lagna_for_business"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lagna in _GOOD_LAGNA,
                          details={"lagna": ctx.lagna})


class StrongMercuryForBusinessRule(MuhurthaRule):
    """Mercury in 1st, 2nd, 7th, 10th, or 11th — commercial acumen."""
    key = "strong_mercury_for_business"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Mercury")
        return RuleResult(occurring=house in {1, 2, 7, 10, 11},
                          details={"mercury_house": house})
