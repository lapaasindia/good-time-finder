"""
Per-category multi-dimensional ranking model.

FinalScore = (
    rule_score         * rule_weight
  + shadbala_bonus     * shadbala_weight
  + gochara_score      * gochara_weight
  + dasha_bonus        * dasha_weight
  + yoga_score         * yoga_weight
  + ashtakavarga_bonus * avarga_weight
)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.core.enums import EventTag


@dataclass(frozen=True)
class CategoryWeights:
    rule: float = 1.0
    shadbala: float = 0.5
    gochara: float = 0.8
    dasha: float = 1.2
    yoga: float = 1.0
    ashtakavarga: float = 0.3


CATEGORY_WEIGHTS: dict[str, CategoryWeights] = {
    "career":      CategoryWeights(rule=0.5, shadbala=0.6, gochara=1.0, dasha=1.5, yoga=0.8, ashtakavarga=0.4),
    "finance":     CategoryWeights(rule=0.5, shadbala=0.5, gochara=1.0, dasha=1.4, yoga=0.8, ashtakavarga=0.5),
    "health":      CategoryWeights(rule=0.6, shadbala=1.0, gochara=1.4, dasha=1.5, yoga=0.6, ashtakavarga=0.4),
    "marriage":    CategoryWeights(rule=0.7, shadbala=0.5, gochara=1.2, dasha=1.2, yoga=1.0, ashtakavarga=0.4),
    "travel":      CategoryWeights(rule=0.8, shadbala=0.3, gochara=1.0, dasha=0.8, yoga=0.4, ashtakavarga=0.3),
    "education":   CategoryWeights(rule=0.6, shadbala=0.6, gochara=1.2, dasha=1.3, yoga=0.8, ashtakavarga=0.4),
    "property":    CategoryWeights(rule=0.6, shadbala=0.5, gochara=1.2, dasha=1.2, yoga=0.6, ashtakavarga=0.4),
    "children":    CategoryWeights(rule=0.7, shadbala=0.5, gochara=1.2, dasha=1.2, yoga=0.8, ashtakavarga=0.4),
    "spirituality":CategoryWeights(rule=0.7, shadbala=0.4, gochara=0.8, dasha=1.0, yoga=1.2, ashtakavarga=0.3),
    "legal":       CategoryWeights(rule=0.6, shadbala=0.6, gochara=1.2, dasha=1.2, yoga=0.6, ashtakavarga=0.4),
    "general":     CategoryWeights(rule=0.5, shadbala=0.4, gochara=1.2, dasha=1.2, yoga=0.8, ashtakavarga=0.4),
}


def get_weights(category: str) -> CategoryWeights:
    return CATEGORY_WEIGHTS.get(category, CategoryWeights())


def compute_composite_score(
    category: str,
    rule_score: float,
    shadbala_bonus: float = 0.0,
    gochara_score: float = 0.0,
    dasha_bonus: float = 0.0,
    yoga_score: float = 0.0,
    ashtakavarga_bonus: float = 0.0,
) -> float:
    w = get_weights(category)
    score = (
        rule_score         * w.rule
        + shadbala_bonus   * w.shadbala
        + gochara_score    * w.gochara
        + dasha_bonus      * w.dasha
        + yoga_score       * w.yoga
        + ashtakavarga_bonus * w.ashtakavarga
    )
    return round(score, 3)


def rank_window(composite_score: float, duration_minutes: float) -> float:
    if duration_minutes <= 0:
        return 0.0
    return round(composite_score * math.log1p(duration_minutes), 3)
