"""
Muhurtha rules for Legal matters — court filings, signing contracts.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {2, 3, 5, 6, 7, 10, 11, 12, 13}
_BAD_LUNAR_DAYS = {4, 8, 9, 14, 15}
_GOOD_WEEKDAYS = {"Sunday", "Monday", "Wednesday", "Thursday"}
_BAD_WEEKDAYS = {"Saturday", "Tuesday"}
_GOOD_NAKSHATRAS = {
    "Ashwini", "Rohini", "Pushya", "Uttara Phalguni",
    "Hasta", "Anuradha", "Shravana", "Revati",
}
_GOOD_LAGNA = {"Aries", "Leo", "Sagittarius", "Libra"}


class GoodLunarDayForLegalRule(MuhurthaRule):
    key = "good_lunar_day_for_legal"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class BadLunarDayForLegalRule(MuhurthaRule):
    key = "bad_lunar_day_for_legal"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _BAD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class GoodWeekdayForLegalRule(MuhurthaRule):
    key = "good_weekday_for_legal"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class BadWeekdayForLegalRule(MuhurthaRule):
    key = "bad_weekday_for_legal"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _BAD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodNakshatraForLegalRule(MuhurthaRule):
    key = "good_nakshatra_for_legal"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class GoodLagnaForLegalRule(MuhurthaRule):
    key = "good_lagna_for_legal"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lagna in _GOOD_LAGNA,
                          details={"lagna": ctx.lagna})


class StrongSunForLegalRule(MuhurthaRule):
    """Sun in 1st, 9th, or 10th house gives authority in legal matters."""

    key = "strong_sun_for_legal"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Sun")
        return RuleResult(occurring=house in {1, 9, 10},
                          details={"sun_house": house})


class SaturnNotInBadHouseLegalRule(MuhurthaRule):
    """Saturn in 6th or 11th (upachaya) is favourable for legal victory."""

    key = "saturn_upachaya_legal"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Saturn")
        return RuleResult(occurring=house in {6, 11},
                          details={"saturn_house": house})
