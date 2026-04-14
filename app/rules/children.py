"""
Muhurtha rules for Children — conception, childbirth planning.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {1, 2, 3, 5, 7, 10, 11, 12, 13}
_BAD_LUNAR_DAYS = {4, 6, 8, 9, 14, 15}
_GOOD_WEEKDAYS = {"Monday", "Thursday", "Friday"}
_BAD_WEEKDAYS = {"Saturday", "Tuesday"}
_GOOD_NAKSHATRAS = {
    "Rohini", "Mrigashira", "Punarvasu", "Pushya",
    "Uttara Phalguni", "Hasta", "Swati", "Anuradha",
    "Uttara Ashadha", "Shravana", "Uttara Bhadrapada", "Revati",
}
_BAD_NAKSHATRAS = {"Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula"}


class GoodLunarDayForChildrenRule(MuhurthaRule):
    key = "good_lunar_day_for_children"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class GoodWeekdayForChildrenRule(MuhurthaRule):
    key = "good_weekday_for_children"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodNakshatraForChildrenRule(MuhurthaRule):
    key = "good_nakshatra_for_children"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class JupiterInFifthHouseRule(MuhurthaRule):
    """Jupiter in 5th house is the strongest indicator for children."""

    key = "jupiter_in_fifth_house"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Jupiter")
        return RuleResult(occurring=house in {5, 9, 1},
                          details={"jupiter_house": house})


class MoonInFertileSignRule(MuhurthaRule):
    """Cancer, Scorpio, Pisces are fertile signs for Moon transit."""

    key = "moon_in_fertile_sign"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_sign in {"Cancer", "Scorpio", "Pisces"},
                          details={"moon_sign": ctx.moon_sign})
