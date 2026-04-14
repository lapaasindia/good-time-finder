"""
Muhurtha rules for Education — starting studies, exams, admissions.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {2, 3, 5, 6, 7, 10, 11, 13}
_BAD_LUNAR_DAYS = {4, 8, 9, 14, 15}
_GOOD_WEEKDAYS = {"Wednesday", "Thursday"}
_BAD_WEEKDAYS = {"Saturday", "Tuesday"}
_GOOD_NAKSHATRAS = {
    "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
    "Uttara Phalguni", "Hasta", "Swati", "Anuradha", "Shravana",
    "Dhanishta", "Uttara Bhadrapada", "Revati",
}
_GOOD_LAGNA = {"Gemini", "Virgo", "Sagittarius", "Aquarius"}


class GoodLunarDayForEducationRule(MuhurthaRule):
    key = "good_lunar_day_for_education"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class GoodWeekdayForEducationRule(MuhurthaRule):
    key = "good_weekday_for_education"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodNakshatraForEducationRule(MuhurthaRule):
    key = "good_nakshatra_for_education"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class GoodLagnaForEducationRule(MuhurthaRule):
    key = "good_lagna_for_education"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lagna in _GOOD_LAGNA,
                          details={"lagna": ctx.lagna})


class StrongMercuryForEducationRule(MuhurthaRule):
    """Mercury in 1st, 4th, or 5th house boosts education outcomes."""

    key = "strong_mercury_for_education"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Mercury")
        return RuleResult(occurring=house in {1, 4, 5},
                          details={"mercury_house": house})


class StrongJupiterForEducationRule(MuhurthaRule):
    """Jupiter in 1st, 4th, 5th, or 9th favours learning."""

    key = "strong_jupiter_for_education"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Jupiter")
        return RuleResult(occurring=house in {1, 4, 5, 9},
                          details={"jupiter_house": house})
