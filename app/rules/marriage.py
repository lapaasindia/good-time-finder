"""
Muhurtha rules for Marriage.
Sources: BV Raman - Muhurtha, classical texts.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {2, 3, 5, 7, 10, 11, 13}

_GOOD_NAKSHATRAS = {
    "Rohini", "Mrigashira", "Magha", "Uttara Phalguni",
    "Hasta", "Swati", "Anuradha", "Uttara Ashadha",
    "Uttara Bhadrapada", "Revati",
}

_GOOD_WEEKDAYS = {"Monday", "Wednesday", "Thursday", "Friday"}


class GoodLunarDayForMarriageRule(MuhurthaRule):
    key = "good_lunar_day_for_marriage"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
            details={"lunar_day": ctx.lunar_day},
        )


class GoodNakshatraForMarriageRule(MuhurthaRule):
    key = "good_nakshatra_for_marriage"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
            details={"nakshatra": ctx.moon_constellation},
        )


class GoodWeekdayForMarriageRule(MuhurthaRule):
    key = "good_weekday_for_marriage"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.weekday in _GOOD_WEEKDAYS,
            details={"weekday": ctx.weekday},
        )
