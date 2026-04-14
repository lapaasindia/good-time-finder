"""
Yoga Engine — detects natal yogas for a person and scores them per category.
"""

from __future__ import annotations

from app.astrology.yogas import YogaResult, detect_all_yogas, yoga_score_for_category
from app.astrology.extra_yogas import detect_all_extra_yogas
from app.astrology.calculations import (
    natal_lagna,
    planet_houses,
    planet_signs,
)
from app.core.models import Person


class YogaEngine:
    def __init__(self, person: Person) -> None:
        self.person = person
        lagna = natal_lagna(person)
        p_houses = planet_houses(person.birth_datetime, person.birth_location)
        p_signs = planet_signs(person.birth_datetime, person.birth_location)
        self._yogas = (
            detect_all_yogas(p_houses, p_signs, lagna) +
            detect_all_extra_yogas(p_houses, p_signs, lagna)
        )
        self._natal_lagna = lagna
        self._natal_planet_houses = p_houses
        self._natal_planet_signs = p_signs

    @property
    def yogas(self) -> list[YogaResult]:
        return self._yogas

    @property
    def active_yogas(self) -> list[YogaResult]:
        return [y for y in self._yogas if y.present]

    def score_for_category(self, category: str) -> float:
        return yoga_score_for_category(self._yogas, category)

    def summary(self) -> dict:
        return {
            "natal_lagna": self._natal_lagna,
            "yogas_found": len(self._yogas),
            "active_count": len(self.active_yogas),
            "active_yogas": [
                {
                    "name": y.name,
                    "present": y.present,
                    "strength": y.strength,
                    "category": y.category,
                    "description": y.description,
                }
                for y in self.active_yogas
            ],
            "all_yogas": [
                {
                    "name": y.name,
                    "present": y.present,
                    "strength": y.strength,
                    "category": y.category,
                    "description": y.description,
                }
                for y in self._yogas
            ],
        }
