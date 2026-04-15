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
    tara: float = 0.4
    chandra_bala: float = 0.3
    avastha: float = 0.3
    pushkara: float = 0.2
    sudarshana: float = 0.4
    jaimini: float = 0.3
    arudha: float = 0.2
    gulika: float = 0.3
    badhaka: float = 0.3


CATEGORY_WEIGHTS: dict[str, CategoryWeights] = {
    "career":      CategoryWeights(rule=0.5, shadbala=0.6, gochara=1.0, dasha=1.5, yoga=0.8, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "finance":     CategoryWeights(rule=0.5, shadbala=0.5, gochara=1.0, dasha=1.4, yoga=0.8, ashtakavarga=0.5, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "health":      CategoryWeights(rule=0.6, shadbala=1.0, gochara=1.4, dasha=1.5, yoga=0.6, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "marriage":    CategoryWeights(rule=0.7, shadbala=0.5, gochara=1.2, dasha=1.2, yoga=1.0, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "travel":      CategoryWeights(rule=0.8, shadbala=0.3, gochara=1.0, dasha=0.8, yoga=0.4, ashtakavarga=0.3, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "education":   CategoryWeights(rule=0.6, shadbala=0.6, gochara=1.2, dasha=1.3, yoga=0.8, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "property":    CategoryWeights(rule=0.6, shadbala=0.5, gochara=1.2, dasha=1.2, yoga=0.6, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "children":    CategoryWeights(rule=0.7, shadbala=0.5, gochara=1.2, dasha=1.2, yoga=0.8, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "spirituality":CategoryWeights(rule=0.7, shadbala=0.4, gochara=0.8, dasha=1.0, yoga=1.2, ashtakavarga=0.3, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "legal":       CategoryWeights(rule=0.6, shadbala=0.6, gochara=1.2, dasha=1.2, yoga=0.6, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "fame":        CategoryWeights(rule=0.5, shadbala=0.7, gochara=1.0, dasha=1.5, yoga=1.0, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "relationships":CategoryWeights(rule=0.7, shadbala=0.5, gochara=1.2, dasha=1.2, yoga=0.8, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "business":    CategoryWeights(rule=0.5, shadbala=0.6, gochara=1.0, dasha=1.4, yoga=0.8, ashtakavarga=0.5, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "accidents":   CategoryWeights(rule=0.6, shadbala=0.8, gochara=1.4, dasha=1.5, yoga=0.6, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
    "general":     CategoryWeights(rule=0.5, shadbala=0.4, gochara=1.2, dasha=1.2, yoga=0.8, ashtakavarga=0.4, tara=0.0, chandra_bala=0.0, avastha=0.0, pushkara=0.0, sudarshana=0.0, jaimini=0.0, arudha=0.0, gulika=0.0, badhaka=0.0),
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
    tara_score: float = 0.0,
    chandra_bala_score: float = 0.0,
    avastha_score: float = 0.0,
    pushkara_bonus_score: float = 0.0,
    sudarshana_score: float = 0.0,
    jaimini_score: float = 0.0,
    arudha_score: float = 0.0,
    gulika_penalty: float = 0.0,
    badhaka_penalty: float = 0.0,
) -> float:
    w = get_weights(category)
    score = (
        rule_score            * w.rule
        + shadbala_bonus      * w.shadbala
        + gochara_score       * w.gochara
        + dasha_bonus         * w.dasha
        + yoga_score          * w.yoga
        + ashtakavarga_bonus  * w.ashtakavarga
        + tara_score          * w.tara
        + chandra_bala_score  * w.chandra_bala
        + avastha_score       * w.avastha
        + pushkara_bonus_score * w.pushkara
        + sudarshana_score    * w.sudarshana
        + jaimini_score       * w.jaimini
        + arudha_score        * w.arudha
        + gulika_penalty      * w.gulika
        + badhaka_penalty     * w.badhaka
    )
    return round(score, 3)


def rank_window(composite_score: float, duration_minutes: float) -> float:
    if duration_minutes <= 0:
        return 0.0
    return round(composite_score * math.log1p(duration_minutes), 3)
