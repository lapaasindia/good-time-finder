"""
Muhurtha rules for Career — job changes, business starts, promotions.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {1, 2, 3, 5, 7, 10, 11, 13}
_BAD_LUNAR_DAYS = {4, 6, 8, 9, 12, 14, 15}
_GOOD_WEEKDAYS = {"Sunday", "Monday", "Thursday"}
_BAD_WEEKDAYS = {"Saturday"}
_GOOD_LAGNA = {"Aries", "Taurus", "Gemini", "Leo", "Virgo", "Sagittarius", "Capricorn"}
_GOOD_NAKSHATRAS = {
    "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Revati",
}
_BAD_NAKSHATRAS = {"Bharani", "Krittika", "Ardra", "Ashlesha", "Jyeshtha", "Mula"}


class GoodLunarDayForCareerRule(MuhurthaRule):
    key = "good_lunar_day_for_career"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class BadLunarDayForCareerRule(MuhurthaRule):
    key = "bad_lunar_day_for_career"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _BAD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class GoodWeekdayForCareerRule(MuhurthaRule):
    key = "good_weekday_for_career"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class BadWeekdayForCareerRule(MuhurthaRule):
    key = "bad_weekday_for_career"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _BAD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodLagnaForCareerRule(MuhurthaRule):
    key = "good_lagna_for_career"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lagna in _GOOD_LAGNA,
                          details={"lagna": ctx.lagna})


class GoodNakshatraForCareerRule(MuhurthaRule):
    key = "good_nakshatra_for_career"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class BadNakshatraForCareerRule(MuhurthaRule):
    key = "bad_nakshatra_for_career"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _BAD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class StrongSunForCareerRule(MuhurthaRule):
    """Sun in 10th or 1st house is excellent for career matters."""

    key = "strong_sun_for_career"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Sun")
        return RuleResult(occurring=house in {1, 10},
                          details={"sun_house": house})


class StrongJupiterForCareerRule(MuhurthaRule):
    """Jupiter in 1st, 9th, or 10th favours career growth."""

    key = "strong_jupiter_for_career"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Jupiter")
        return RuleResult(occurring=house in {1, 9, 10},
                          details={"jupiter_house": house})
