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
import os
import pickle
import numpy as np

# Load Random Forest Model
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "rf_life_predictor.pkl")
_rf_model = None

try:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            _rf_model = pickle.load(f)
except Exception as e:
    print(f"Failed to load RF model: {e}")

USE_ML_MODEL = True  # Toggle this to use classical linear weights vs ML
ML_CLASSICAL_BLEND = 0.08


from app.core.enums import EventTag


@dataclass(frozen=True)
class CategoryWeights:
    rule: float = 1.0
    shadbala: float = 1.0
    gochara: float = 1.0
    dasha: float = 1.0
    yoga: float = 1.0
    ashtakavarga: float = 1.0
    panchang: float = 0.2
    tara: float = 1.0
    chandra_bala: float = 1.0
    avastha: float = 1.0
    pushkara: float = 1.0
    sudarshana: float = 1.0
    jaimini: float = 1.0
    arudha: float = 1.0
    gulika: float = 1.0
    badhaka: float = 1.0
    bhrigu: float = 1.0
    kp: float = 1.0
    kp_cuspal: float = 1.0
    double_transit: float = 1.0
    gochara_house_specific: float = 1.0
    planet_focus: float = 1.0


CATEGORY_WEIGHTS: dict[str, CategoryWeights] = {
    "career":     CategoryWeights(rule=1.26, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "finance":     CategoryWeights(rule=1.27, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "health":     CategoryWeights(rule=1.28, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "marriage":     CategoryWeights(rule=1.29, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "travel":     CategoryWeights(rule=1.30, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "education":     CategoryWeights(rule=1.31, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "property":     CategoryWeights(rule=1.32, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "children":     CategoryWeights(rule=1.33, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "spirituality":     CategoryWeights(rule=1.34, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "legal":     CategoryWeights(rule=1.35, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "fame":     CategoryWeights(rule=1.36, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "relationships":     CategoryWeights(rule=1.37, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "business":     CategoryWeights(rule=1.38, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "accidents":     CategoryWeights(rule=1.39, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
    "general":     CategoryWeights(rule=1.40, shadbala=0.40, gochara=0.81, dasha=1.40, yoga=1.26, ashtakavarga=0.10, tara=0.17, chandra_bala=0.00, avastha=0.00, pushkara=0.05, sudarshana=0.07, jaimini=0.19, arudha=0.13, gulika=0.00, badhaka=0.08, bhrigu=1.05, kp=0.46),
}


def get_weights(category: str) -> CategoryWeights:
    return CATEGORY_WEIGHTS.get(category, CategoryWeights())


def _feature_row(
    rule_score: float = 0.0,
    shadbala_bonus: float = 0.0,
    gochara_score: float = 0.0,
    dasha_bonus: float = 0.0,
    yoga_score: float = 0.0,
    ashtakavarga_bonus: float = 0.0,
    panchang_score: float = 0.0,
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
    kp_cuspal_score: float = 0.0,
    double_transit: float = 0.0,
    gochara_house_specific: float = 0.0,
    planet_focus: float = 0.0,
) -> list[float]:
    return [
        rule_score,
        shadbala_bonus,
        gochara_score,
        dasha_bonus,
        yoga_score,
        ashtakavarga_bonus,
        panchang_score,
        tara_score,
        chandra_bala_score,
        avastha_score,
        pushkara_bonus_score,
        sudarshana_score,
        jaimini_score,
        arudha_score,
        gulika_penalty,
        badhaka_penalty,
        bhrigu_bonus,
        kp_score,
        kp_cuspal_score,
        double_transit,
        gochara_house_specific,
        planet_focus,
    ]


def _classical_score_from_row(category: str, row: list[float]) -> float:
    w = get_weights(category)
    # Support both legacy 19-col and new 22-col rows
    if len(row) == 19:
        # Legacy: ashtakavarga was ashtakavarga+panchang merged; no house_specific/planet_focus
        (
            rule_score, shadbala_bonus, gochara_score, dasha_bonus, yoga_score,
            ashtakavarga_bonus, tara_score, chandra_bala_score, avastha_score,
            pushkara_bonus_score, sudarshana_score, jaimini_score, arudha_score,
            gulika_penalty, badhaka_penalty, bhrigu_bonus, kp_score, kp_cuspal_score,
            double_transit,
        ) = row
        panchang_score = 0.0
        gochara_house_specific = 0.0
        planet_focus = 0.0
    else:
        (
            rule_score, shadbala_bonus, gochara_score, dasha_bonus, yoga_score,
            ashtakavarga_bonus, panchang_score, tara_score, chandra_bala_score,
            avastha_score, pushkara_bonus_score, sudarshana_score, jaimini_score,
            arudha_score, gulika_penalty, badhaka_penalty, bhrigu_bonus, kp_score,
            kp_cuspal_score, double_transit, gochara_house_specific, planet_focus,
        ) = row
    return (
        rule_score * w.rule
        + shadbala_bonus * w.shadbala
        + gochara_score * w.gochara
        + dasha_bonus * w.dasha
        + yoga_score * w.yoga
        + ashtakavarga_bonus * w.ashtakavarga
        + panchang_score * w.panchang
        + tara_score * w.tara
        + chandra_bala_score * w.chandra_bala
        + avastha_score * w.avastha
        + pushkara_bonus_score * w.pushkara
        + sudarshana_score * w.sudarshana
        + jaimini_score * w.jaimini
        + arudha_score * w.arudha
        + gulika_penalty * w.gulika
        + badhaka_penalty * w.badhaka
        + bhrigu_bonus * w.bhrigu
        + kp_score * w.kp
        + kp_cuspal_score * w.kp_cuspal
        + double_transit * w.double_transit
        + gochara_house_specific * w.gochara_house_specific
        + planet_focus * w.planet_focus
    )


def _category_offset(category: str) -> float:
    return 1.0 if category in ("general", "accidents") else 0.0


def compute_composite_score(
    category: str,
    rule_score: float = 0.0,
    shadbala_bonus: float = 0.0,
    gochara_score: float = 0.0,
    dasha_bonus: float = 0.0,
    yoga_score: float = 0.0,
    ashtakavarga_bonus: float = 0.0,
    panchang_score: float = 0.0,
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
    kp_cuspal_score: float = 0.0,
    double_transit: float = 0.0,
    gochara_house_specific: float = 0.0,
    planet_focus: float = 0.0,
) -> float:
    row = _feature_row(
        rule_score,
        shadbala_bonus,
        gochara_score,
        dasha_bonus,
        yoga_score,
        ashtakavarga_bonus,
        panchang_score,
        tara_score,
        chandra_bala_score,
        avastha_score,
        pushkara_bonus_score,
        sudarshana_score,
        jaimini_score,
        arudha_score,
        gulika_penalty,
        badhaka_penalty,
        bhrigu_bonus,
        kp_score,
        kp_cuspal_score,
        double_transit,
        gochara_house_specific,
        planet_focus,
    )
    if USE_ML_MODEL and _rf_model is not None:
        features = np.array([row[:22]], dtype=np.float64)
        # predict_proba returns [P(Bad), P(Good)]
        probs = _rf_model.predict_proba(features)[0]
        # Map probability [0,1] to a score [-3.0, 3.0] roughly
        p_good = probs[1]

        classical_score = _classical_score_from_row(category, row)
        ml_score = (p_good - 0.5) * 6.0  # -3.0 to +3.0

        # Blend a light classical component back in so the ML path keeps
        # category weighting and signal magnitude context instead of collapsing
        score = 0.8 * ml_score + 0.2 * classical_score
    else:
        score = _classical_score_from_row(category, row)

    # Offset adjustments for categories that skew too negative naturally
    score += _category_offset(category)

    # Clamp the raw score to [-3.0, 3.0] to prevent unbounded composites
    return max(-3.0, min(3.0, round(score, 3)))


def batch_composite_scores(
    category: str,
    feature_rows: list[list[float]],
) -> list[float]:
    """Vectorised scoring — one RF call for all slots."""
    if not feature_rows:
        return []

    offset = _category_offset(category)

    if USE_ML_MODEL and _rf_model is not None:
        trimmed_rows = [r[:22] for r in feature_rows]
        X = np.array(trimmed_rows, dtype=np.float64)
        probs = _rf_model.predict_proba(X)[:, 1]  # P(Good)
        classical_scores = np.array(
            [_classical_score_from_row(category, row) for row in feature_rows],
            dtype=np.float64,
        )
        ml_scores = (probs - 0.5) * 6.0
        scores = 0.8 * ml_scores + 0.2 * classical_scores + offset
        return [max(-3.0, min(3.0, round(float(s), 3))) for s in scores]

    # Classical fallback
    results: list[float] = []
    for row in feature_rows:
        score = _classical_score_from_row(category, row) + offset
        results.append(round(score, 3))
    return results


def rank_window(composite_score: float, duration_minutes: float) -> float:
    if duration_minutes <= 0:
        return 0.0
    return round(composite_score * math.log1p(duration_minutes), 3)
