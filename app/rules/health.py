"""
Muhurtha rules for Health — medical procedures, surgery, treatments.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {1, 2, 3, 5, 6, 7, 10, 11, 12, 13}
_BAD_LUNAR_DAYS = {8, 9, 14, 15}
_GOOD_WEEKDAYS = {"Monday", "Wednesday", "Thursday"}
_BAD_WEEKDAYS_SURGERY = {"Saturday", "Tuesday", "Sunday"}
_GOOD_NAKSHATRAS = {
    "Ashwini", "Mrigashira", "Punarvasu", "Pushya",
    "Hasta", "Anuradha", "Shravana", "Revati",
}
_BAD_NAKSHATRAS_FOR_SURGERY = {
    "Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula", "Purva Ashadha",
}

_SIGN_BODY_PARTS: dict[str, str] = {
    "Aries": "Head", "Taurus": "Throat/Neck", "Gemini": "Chest/Arms",
    "Cancer": "Stomach", "Leo": "Heart/Spine", "Virgo": "Intestines",
    "Libra": "Kidneys", "Scorpio": "Reproductive organs", "Sagittarius": "Thighs",
    "Capricorn": "Knees", "Aquarius": "Calves", "Pisces": "Feet",
}


class GoodLunarDayForHealthRule(MuhurthaRule):
    key = "good_lunar_day_for_health"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class BadLunarDayForSurgeryRule(MuhurthaRule):
    key = "bad_lunar_day_for_surgery"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _BAD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class GoodWeekdayForHealthRule(MuhurthaRule):
    key = "good_weekday_for_health"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class BadWeekdayForSurgeryRule(MuhurthaRule):
    key = "bad_weekday_for_surgery"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _BAD_WEEKDAYS_SURGERY,
                          details={"weekday": ctx.weekday})


class GoodNakshatraForHealthRule(MuhurthaRule):
    key = "good_nakshatra_for_health"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class BadNakshatraForSurgeryRule(MuhurthaRule):
    key = "bad_nakshatra_for_surgery"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _BAD_NAKSHATRAS_FOR_SURGERY,
                          details={"nakshatra": ctx.moon_constellation})


class MoonNotInLagnaSignRule(MuhurthaRule):
    """Avoid surgery when Moon is in the sign governing the body part being operated."""

    key = "moon_not_in_lagna_sign_surgery"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        occurring = ctx.moon_sign == ctx.lagna
        return RuleResult(occurring=occurring,
                          details={"moon_sign": ctx.moon_sign, "lagna": ctx.lagna})


class StrongMoonForHealthRule(MuhurthaRule):
    """Moon in 1st, 4th, 7th, or 10th (Kendra) is generally beneficial for health."""

    key = "strong_moon_for_health"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Moon")
        return RuleResult(occurring=house in {1, 4, 7, 10},
                          details={"moon_house": house})
