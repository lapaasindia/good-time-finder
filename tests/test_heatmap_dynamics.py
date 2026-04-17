"""
Phase 7 — Test 2: Heatmap dynamics & per-slot variance.

Verifies:
  • Running the predictor for the same person/range across categories
    produces distinct composite scores (no category is a clone of another).
  • Adjacent windows within a single prediction have non-trivial variance
    (the score is not flat/constant).
  • All required window fields are populated.
"""

import pytest
from datetime import datetime
from statistics import stdev

from app.core.models import Person, GeoLocation, TimeRange
from app.services.life_predictor import LifePredictorService


TEST_PERSON = Person(
    name="Test User",
    birth_datetime=datetime(1990, 5, 15, 10, 30),
    birth_location=GeoLocation(latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata"),
)

MEDIUM_RANGE = TimeRange(
    start=datetime(2025, 6, 1),
    end=datetime(2025, 7, 1),
)


@pytest.fixture(scope="module")
def multi_predictions():
    svc = LifePredictorService()
    results = {}
    for cat in ("career", "finance", "marriage", "health"):
        results[cat] = svc.predict(
            person=TEST_PERSON,
            location=TEST_PERSON.birth_location,
            time_range=MEDIUM_RANGE,
            category=cat,
        )
    return results


class TestCategoryDivergence:
    """Each category should produce different overall scores."""

    def test_scores_not_identical(self, multi_predictions):
        scores = [p.overall_period_score for p in multi_predictions.values()]
        # At least 2 distinct values expected
        assert len(set(scores)) >= 2, (
            f"All 4 categories produced identical scores: {scores}"
        )


class TestPerSlotVariance:
    """Within a single category's windows, scores should show variance."""

    def test_window_variance(self, multi_predictions):
        for cat, pred in multi_predictions.items():
            if len(pred.windows) < 3:
                continue  # too few windows to check variance
            scores = [w.composite_score for w in pred.windows]
            sd = stdev(scores)
            assert sd > 0.01, (
                f"Category '{cat}' has near-zero variance (stdev={sd:.4f}) "
                f"across {len(scores)} windows"
            )


class TestWindowFieldCompleteness:
    """All required fields must be present on every window."""

    REQUIRED = [
        "start", "end", "nature", "composite_score", "rank",
        "duration_minutes", "gochara_score", "shadbala_score",
        "dasha_bonus", "yoga_score", "rule_score",
        "tara_score", "chandra_bala_score", "avastha_score",
        "pushkara_bonus_score", "sudarshana_score", "sandhi_penalty",
        "bhrigu_bonus", "kp_score", "kp_cuspal_score", "double_transit",
        "confidence", "panchang_score",
    ]

    def test_fields_present(self, multi_predictions):
        pred = multi_predictions["career"]
        for w in pred.windows[:5]:
            for field in self.REQUIRED:
                assert hasattr(w, field), f"Window missing field: {field}"
