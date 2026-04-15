"""
Muhurtha rules for Relationships — broader than marriage: friendships,
partnerships, social bonds, romantic connections.

Key houses: 5th (romance), 7th (partnerships), 11th (social circle)
Key planets: Venus (love/beauty), Moon (emotions), Jupiter (goodwill), Mercury (communication)
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_GOOD_NAKSHATRAS = {
    "Rohini", "Mrigashira", "Punarvasu", "Pushya", "Uttara Phalguni",
    "Hasta", "Swati", "Anuradha", "Shravana", "Uttara Bhadrapada", "Revati",
}
_BAD_NAKSHATRAS = {"Bharani", "Ardra", "Ashlesha", "Jyeshtha", "Mula"}

_GOOD_WEEKDAYS = {"Monday", "Wednesday", "Thursday", "Friday"}

_GOOD_LAGNA = {"Taurus", "Cancer", "Libra", "Sagittarius", "Pisces"}


class GoodNakshatraForRelationshipsRule(MuhurthaRule):
    key = "good_nakshatra_for_relationships"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _GOOD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class BadNakshatraForRelationshipsRule(MuhurthaRule):
    key = "bad_nakshatra_for_relationships"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _BAD_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class GoodWeekdayForRelationshipsRule(MuhurthaRule):
    key = "good_weekday_for_relationships"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _GOOD_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class GoodLagnaForRelationshipsRule(MuhurthaRule):
    key = "good_lagna_for_relationships"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.lagna in _GOOD_LAGNA,
                          details={"lagna": ctx.lagna})


class VenusInGoodHouseForRelationshipsRule(MuhurthaRule):
    """Venus in 1st, 5th, 7th, or 11th — strong romantic and social magnetism."""
    key = "venus_in_good_house_relationships"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Venus")
        return RuleResult(occurring=house in {1, 5, 7, 11},
                          details={"venus_house": house})


class MoonInGoodHouseForRelationshipsRule(MuhurthaRule):
    """Moon in Kendra (1,4,7,10) — emotional receptivity and social connections."""
    key = "moon_in_good_house_relationships"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Moon")
        return RuleResult(occurring=house in {1, 4, 7, 10},
                          details={"moon_house": house})
