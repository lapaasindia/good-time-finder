from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.models import AstroContext, Person, RuleResult


class MuhurthaRule(ABC):
    key: str

    @abstractmethod
    def evaluate(self, ctx: AstroContext, person: Person) -> RuleResult:
        pass

    def __repr__(self) -> str:
        return f"<Rule: {self.key}>"
