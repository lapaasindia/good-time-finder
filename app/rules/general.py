"""
General muhurtha rules applicable across all activity types.
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

_BENEFIC_SIGNS = {"Taurus", "Cancer", "Virgo", "Libra", "Sagittarius", "Pisces"}
_MALEFIC_SIGNS = {"Aries", "Scorpio", "Capricorn", "Aquarius"}

_JUPITER_GOOD_HOUSES = {1, 4, 5, 7, 9, 10, 11}
_SATURN_BAD_HOUSES = {1, 4, 7, 8, 12}


class GoodMoonSignRule(MuhurthaRule):
    """Moon transiting a benefic sign is generally auspicious."""

    key = "good_moon_sign_general"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.moon_sign in _BENEFIC_SIGNS,
            details={"moon_sign": ctx.moon_sign},
        )


class BadMoonSignRule(MuhurthaRule):
    """Moon transiting a malefic sign is generally inauspicious."""

    key = "bad_moon_sign_general"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(
            occurring=ctx.moon_sign in _MALEFIC_SIGNS,
            details={"moon_sign": ctx.moon_sign},
        )


class JupiterInGoodHouseRule(MuhurthaRule):
    """Jupiter placed in auspicious houses is favourable."""

    key = "jupiter_in_good_house"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Jupiter")
        if house is None:
            return RuleResult(occurring=False)
        return RuleResult(
            occurring=house in _JUPITER_GOOD_HOUSES,
            details={"jupiter_house": house},
        )


class SaturnInBadHouseRule(MuhurthaRule):
    """Saturn in Dusthana (bad) houses is unfavourable."""

    key = "saturn_in_bad_house"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Saturn")
        if house is None:
            return RuleResult(occurring=False)
        return RuleResult(
            occurring=house in _SATURN_BAD_HOUSES,
            details={"saturn_house": house},
        )
