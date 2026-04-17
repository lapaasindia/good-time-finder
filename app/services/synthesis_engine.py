"""
Synthesis Engine — The Core Narrative Constructor
Aggregates Parashari, Jaimini, Nadi, KP, and Bhrigu scores to output a unified "Jury" prediction
for specific life domains.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.domain_scorer import DomainScore, ScoringContext, score_domain

class SynthesisEngine:
    def __init__(
        self,
        ctx: ScoringContext
    ):
        self.ctx = ctx

    def synthesize(self, category: str, name_en: str, name_hi: str) -> DomainScore:
        score = score_domain(category, self.ctx)
        # We override the category name for display in the report
        score.category = name_en
        # Store hindi name on the object as well
        setattr(score, "domain_hi", name_hi)
        return score

    def run_all(self) -> list[DomainScore]:
        return [
            self.synthesize("career", "Career & Profession (Karma Bhava)", "करियर और पेशा (कर्म भाव)"),
            self.synthesize("finance", "Wealth & Finances (Dhana & Labha Bhava)", "धन और वित्त (धन और लाभ भाव)"),
            self.synthesize("marriage", "Marriage & Relationships (Kalatra Bhava)", "विवाह और रिश्ते (कलत्र भाव)"),
            self.synthesize("health", "Health & Well-being (Tanu Bhava)", "स्वास्थ्य और भलाई (तनु भाव)"),
            self.synthesize("education", "Education & Knowledge (Vidya Bhava)", "शिक्षा और ज्ञान (विद्या भाव)"),
            self.synthesize("children", "Children & Creativity (Putra Bhava)", "बच्चे और रचनात्मकता (पुत्र भाव)"),
            self.synthesize("property", "Property & Vehicles (Sukha Bhava)", "संपत्ति और वाहन (सुख भाव)"),
            self.synthesize("spirituality", "Spirituality & Luck (Dharma Bhava)", "आध्यात्मिकता और भाग्य (धर्म भाव)"),
            self.synthesize("legal", "Legal & Competitors (Ari Bhava)", "कानूनी और प्रतियोगी (अरि भाव)"),
            self.synthesize("travel", "Travel & Foreign (Vyaya & Bhagya)", "यात्रा और विदेश (व्यय और भाग्य)"),
        ]
