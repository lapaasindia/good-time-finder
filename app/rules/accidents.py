"""
Muhurtha rules for Accidents — mishaps, danger, injury, theft.

Note: For this category, "good" means BAD (accident-prone) and scoring is
inverted. Planets that are malefic for most categories are RELEVANT here.

Key houses: 6th (enemies/injury), 8th (sudden events), 12th (loss)
Key planets: Mars (violence/fire), Saturn (falls/chronic), Rahu (sudden), Ketu (hidden)
"""

from __future__ import annotations

from app.core.models import AstroContext, Person, RuleResult
from app.rules.base import MuhurthaRule

# Nakshatras associated with danger and violence
_DANGEROUS_NAKSHATRAS = {
    "Bharani", "Ardra", "Ashlesha", "Magha",
    "Jyeshtha", "Mula", "Purva Ashadha",
}
_SAFE_NAKSHATRAS = {
    "Ashwini", "Rohini", "Pushya", "Hasta",
    "Anuradha", "Shravana", "Revati",
}

_DANGEROUS_WEEKDAYS = {"Tuesday", "Saturday"}
_SAFE_WEEKDAYS = {"Thursday", "Friday"}


class DangerousNakshatraRule(MuhurthaRule):
    """Nakshatras associated with violence, sudden events, or danger."""
    key = "dangerous_nakshatra_accidents"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _DANGEROUS_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class SafeNakshatraRule(MuhurthaRule):
    """Nakshatras that indicate relative safety and protection."""
    key = "safe_nakshatra_accidents"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.moon_constellation in _SAFE_NAKSHATRAS,
                          details={"nakshatra": ctx.moon_constellation})


class DangerousWeekdayRule(MuhurthaRule):
    """Tuesday (Mars) and Saturday (Saturn) carry higher accident risk."""
    key = "dangerous_weekday_accidents"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _DANGEROUS_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class SafeWeekdayRule(MuhurthaRule):
    """Thursday (Jupiter) and Friday (Venus) offer protection."""
    key = "safe_weekday_accidents"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        return RuleResult(occurring=ctx.weekday in _SAFE_WEEKDAYS,
                          details={"weekday": ctx.weekday})


class MarsInDangerHouseRule(MuhurthaRule):
    """Mars in 1st, 6th, 8th, or 12th house — heightened injury risk."""
    key = "mars_in_danger_house"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Mars")
        return RuleResult(occurring=house in {1, 6, 8, 12},
                          details={"mars_house": house})


class SaturnInDangerHouseRule(MuhurthaRule):
    """Saturn in 1st, 4th, 8th, or 12th — risk of falls, chronic issues."""
    key = "saturn_in_danger_house"

    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        house = ctx.planet_houses.get("Saturn")
        return RuleResult(occurring=house in {1, 4, 8, 12},
                          details={"saturn_house": house})
