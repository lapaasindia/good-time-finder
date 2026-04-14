from __future__ import annotations

from app.rules.base import MuhurthaRule


class RuleRegistry:
    def __init__(self) -> None:
        self._rules: dict[str, MuhurthaRule] = {}

    def register(self, rule: MuhurthaRule) -> None:
        self._rules[rule.key] = rule

    def get(self, key: str) -> MuhurthaRule:
        if key not in self._rules:
            raise KeyError(f"No rule registered for key '{key}'")
        return self._rules[key]

    def all_keys(self) -> list[str]:
        return list(self._rules.keys())


def build_default_registry() -> RuleRegistry:
    from app.rules.travel import (
        BadConstellationForTravelRule,
        BadLunarDayForTravelRule,
        BadWeekdayForTravelRule,
        BestLagnaForTravelRule,
        GoodConstellationForTravelRule,
        GoodLagnaForTravelRule,
        GoodLunarDayForTravelRule,
        GoodWeekdayForTravelRule,
    )
    from app.rules.general import (
        GoodMoonSignRule,
        BadMoonSignRule,
        JupiterInGoodHouseRule,
        SaturnInBadHouseRule,
    )
    from app.rules.marriage import (
        GoodLunarDayForMarriageRule,
        GoodNakshatraForMarriageRule,
        GoodWeekdayForMarriageRule,
    )
    from app.rules.career import (
        GoodLunarDayForCareerRule,
        BadLunarDayForCareerRule,
        GoodWeekdayForCareerRule,
        BadWeekdayForCareerRule,
        GoodLagnaForCareerRule,
        GoodNakshatraForCareerRule,
        BadNakshatraForCareerRule,
        StrongSunForCareerRule,
        StrongJupiterForCareerRule,
    )
    from app.rules.finance import (
        GoodLunarDayForFinanceRule,
        BadLunarDayForFinanceRule,
        GoodWeekdayForFinanceRule,
        GoodNakshatraForFinanceRule,
        GoodLagnaForFinanceRule,
        JupiterInWealthHouseRule,
        VenusInGoodHouseForFinanceRule,
    )
    from app.rules.health import (
        GoodLunarDayForHealthRule,
        BadLunarDayForSurgeryRule,
        GoodWeekdayForHealthRule,
        BadWeekdayForSurgeryRule,
        GoodNakshatraForHealthRule,
        BadNakshatraForSurgeryRule,
        MoonNotInLagnaSignRule,
        StrongMoonForHealthRule,
    )
    from app.rules.education import (
        GoodLunarDayForEducationRule,
        GoodWeekdayForEducationRule,
        GoodNakshatraForEducationRule,
        GoodLagnaForEducationRule,
        StrongMercuryForEducationRule,
        StrongJupiterForEducationRule,
    )
    from app.rules.property import (
        GoodLunarDayForPropertyRule,
        GoodWeekdayForPropertyRule,
        GoodNakshatraForPropertyRule,
        GoodLagnaForPropertyRule,
        MarsInGoodHouseForPropertyRule,
        StrongMoonForPropertyRule,
    )
    from app.rules.children import (
        GoodLunarDayForChildrenRule,
        GoodWeekdayForChildrenRule,
        GoodNakshatraForChildrenRule,
        JupiterInFifthHouseRule,
        MoonInFertileSignRule,
    )
    from app.rules.spirituality import (
        GoodLunarDayForSpiritualityRule,
        GoodWeekdayForSpiritualityRule,
        GoodNakshatraForSpiritualityRule,
        SpiritualLagnaRule,
        JupiterInSpiritualHouseRule,
        KetuInSpiritualHouseRule,
    )
    from app.rules.legal import (
        GoodLunarDayForLegalRule,
        BadLunarDayForLegalRule,
        GoodWeekdayForLegalRule,
        BadWeekdayForLegalRule,
        GoodNakshatraForLegalRule,
        GoodLagnaForLegalRule,
        StrongSunForLegalRule,
        SaturnNotInBadHouseLegalRule,
    )

    registry = RuleRegistry()

    for rule in [
        GoodLunarDayForTravelRule(), BadLunarDayForTravelRule(),
        GoodConstellationForTravelRule(), BadConstellationForTravelRule(),
        GoodLagnaForTravelRule(), BestLagnaForTravelRule(),
        GoodWeekdayForTravelRule(), BadWeekdayForTravelRule(),
        GoodMoonSignRule(), BadMoonSignRule(),
        JupiterInGoodHouseRule(), SaturnInBadHouseRule(),
        GoodLunarDayForMarriageRule(), GoodNakshatraForMarriageRule(), GoodWeekdayForMarriageRule(),
        GoodLunarDayForCareerRule(), BadLunarDayForCareerRule(),
        GoodWeekdayForCareerRule(), BadWeekdayForCareerRule(),
        GoodLagnaForCareerRule(), GoodNakshatraForCareerRule(), BadNakshatraForCareerRule(),
        StrongSunForCareerRule(), StrongJupiterForCareerRule(),
        GoodLunarDayForFinanceRule(), BadLunarDayForFinanceRule(),
        GoodWeekdayForFinanceRule(), GoodNakshatraForFinanceRule(), GoodLagnaForFinanceRule(),
        JupiterInWealthHouseRule(), VenusInGoodHouseForFinanceRule(),
        GoodLunarDayForHealthRule(), BadLunarDayForSurgeryRule(),
        GoodWeekdayForHealthRule(), BadWeekdayForSurgeryRule(),
        GoodNakshatraForHealthRule(), BadNakshatraForSurgeryRule(),
        MoonNotInLagnaSignRule(), StrongMoonForHealthRule(),
        GoodLunarDayForEducationRule(), GoodWeekdayForEducationRule(),
        GoodNakshatraForEducationRule(), GoodLagnaForEducationRule(),
        StrongMercuryForEducationRule(), StrongJupiterForEducationRule(),
        GoodLunarDayForPropertyRule(), GoodWeekdayForPropertyRule(),
        GoodNakshatraForPropertyRule(), GoodLagnaForPropertyRule(),
        MarsInGoodHouseForPropertyRule(), StrongMoonForPropertyRule(),
        GoodLunarDayForChildrenRule(), GoodWeekdayForChildrenRule(),
        GoodNakshatraForChildrenRule(), JupiterInFifthHouseRule(), MoonInFertileSignRule(),
        GoodLunarDayForSpiritualityRule(), GoodWeekdayForSpiritualityRule(),
        GoodNakshatraForSpiritualityRule(), SpiritualLagnaRule(),
        JupiterInSpiritualHouseRule(), KetuInSpiritualHouseRule(),
        GoodLunarDayForLegalRule(), BadLunarDayForLegalRule(),
        GoodWeekdayForLegalRule(), BadWeekdayForLegalRule(),
        GoodNakshatraForLegalRule(), GoodLagnaForLegalRule(),
        StrongSunForLegalRule(), SaturnNotInBadHouseLegalRule(),
    ]:
        registry.register(rule)

    return registry
