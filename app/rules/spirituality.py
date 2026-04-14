"""
Muhurtha rules for Spirituality — meditation, initiation, pilgrimage.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_LUNAR_DAYS = {1, 5, 6, 7, 8, 11, 12, 13, 14, 15}
_GOOD_WEEKDAYS = {"Monday", "Thursday", "Saturday"}
_GOOD_NAKSHATRAS = {
    "Ashwini", "Rohini", "Punarvasu", "Pushya", "Uttara Phalguni",
    "Hasta", "Anuradha", "Uttara Ashadha", "Shravana",
    "Uttara Bhadrapada", "Revati",
}
_SPIRITUAL_LAGNA = {"Cancer", "Sagittarius", "Pisces", "Aquarius"}


class GoodLunarDayForSpiritualityRule(MuhurthaRule):
    key = "good_lunar_day_for_spirituality"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lunar_day in _GOOD_LUNAR_DAYS,
                          details={"lunar_day": ctx.lunar_day})


class GoodWeekdayForSpiritualityRule(MuhurthaRule):
    key = "good_weekday_for_spirituality"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodNakshatraForSpiritualityRule(MuhurthaRule):
    key = "good_nakshatra_for_spirituality"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class SpiritualLagnaRule(MuhurthaRule):
    key = "spiritual_lagna"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lagna in _SPIRITUAL_LAGNA,
                          details={"lagna": ctx.lagna})


class JupiterInSpiritualHouseRule(MuhurthaRule):
    """Jupiter in 9th, 12th, or 1st house strengthens spiritual practices."""

    key = "jupiter_in_spiritual_house"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Jupiter")
        return RuleResult(occurring=house in {1, 9, 12},
                          details={"jupiter_house": house})


class KetuInSpiritualHouseRule(MuhurthaRule):
    """Ketu in 9th or 12th indicates strong spiritual inclination."""

    key = "ketu_in_spiritual_house"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Ketu")
        return RuleResult(occurring=house in {9, 12},
                          details={"ketu_house": house})
