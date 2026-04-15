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
    bhrigu: float = 1.0
    kp: float = 0.5


CATEGORY_WEIGHTS: dict[str, CategoryWeights] = {
    "career":      CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "finance":     CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "health":      CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "marriage":    CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "travel":      CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "education":   CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "property":    CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "children":    CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "spirituality":CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "legal":       CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "fame":        CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "relationships":CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "business":    CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "accidents":   CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "general":     CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
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
    bhrigu_bonus: float = 0.0,
    kp_score: float = 0.0,
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
        + bhrigu_bonus        * w.bhrigu
        + kp_score            * w.kp
    )
    return round(score, 3)


def rank_window(composite_score: float, duration_minutes: float) -> float:
    if duration_minutes <= 0:
        return 0.0
    return round(composite_score * math.log1p(duration_minutes), 3)
