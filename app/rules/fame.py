"""
Muhurtha rules for Fame — public recognition, awards, media attention.

Key houses: 1st (self), 5th (creativity), 9th (fortune), 10th (status), 11th (gains)
Key planets: Sun (authority/recognition), Jupiter (honour), Venus (arts), Moon (public)
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_NAKSHATRAS = {
    "Ashwini", "Rohini", "Pushya", "Magha", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Anuradha", "Shravana",
    "Dhanishta", "Revati",
}
_BAD_NAKSHATRAS = {"Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula"}

_GOOD_WEEKDAYS = {"Sunday", "Thursday", "Monday"}
_BAD_WEEKDAYS = {"Saturday"}

_GOOD_LAGNA = {"Leo", "Aries", "Sagittarius", "Taurus", "Libra"}


class GoodNakshatraForFameRule(MuhurthaRule):
    key = "good_nakshatra_for_fame"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class BadNakshatraForFameRule(MuhurthaRule):
    key = "bad_nakshatra_for_fame"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _BAD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class GoodWeekdayForFameRule(MuhurthaRule):
    key = "good_weekday_for_fame"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class BadWeekdayForFameRule(MuhurthaRule):
    key = "bad_weekday_for_fame"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _BAD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodLagnaForFameRule(MuhurthaRule):
    key = "good_lagna_for_fame"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lagna in _GOOD_LAGNA,
                          details={"lagna": ctx.lagna})


class StrongSunForFameRule(MuhurthaRule):
    """Sun in 1st, 10th, or 11th house — strong public authority and recognition."""
    key = "strong_sun_for_fame"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Sun")
        return RuleResult(occurring=house in {1, 10, 11},
                          details={"sun_house": house})


class JupiterInFameHouseRule(MuhurthaRule):
    """Jupiter in 1st, 5th, 9th, or 10th — honour, awards, public acclaim."""
    key = "jupiter_in_fame_house"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Jupiter")
        return RuleResult(occurring=house in {1, 5, 9, 10},
                          details={"jupiter_house": house})
