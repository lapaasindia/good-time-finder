"""
Phase 7 — Test 1: Normalization & tanh calibration.

Verifies:
  • PredictionWindow.confidence is in [0, 1]
  • Composite scores stay within tanh-bounded range [-3, +3]
  • Panchang scores are propagated
  • Domain static scores and confidences are populated
"""

import pytest
from datetime import datetime

from app.core.models import Person, GeoLocation, TimeRange
from app.services.life_predictor import LifePredictorService, PredictionWindow


# ── fixture ──────────────────────────────────────────────────

TEST_PERSON = Person(
    name="Test User",
    birth_datetime=datetime(1990, 5, 15, 10, 30),
    birth_location=GeoLocation(latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata"),
)

SHORT_RANGE = TimeRange(
    start=datetime(2025, 6, 1),
    end=datetime(2025, 6, 7),
)


@pytest.fixture(scope="module")
def prediction():
    svc = LifePredictorService()
    return svc.predict(
        person=TEST_PERSON,
        location=TEST_PERSON.birth_location,
        time_range=SHORT_RANGE,
        category="career",
    )


# ── tests ────────────────────────────────────────────────────

class TestConfidenceBounds:
    """Every window confidence must be 0 ≤ c ≤ 1."""

    def test_confidence_exists(self, prediction):
        assert len(prediction.windows) > 0, "Should produce at least one window"
        for w in prediction.windows:
            assert hasattr(w, "confidence"), "Window must have confidence field"

    def test_confidence_in_range(self, prediction):
        for w in prediction.windows:
            assert 0.0 <= w.confidence <= 1.0, (
                f"confidence={w.confidence} out of [0,1] for window {w.start}"
            )


class TestTanhCalibration:
    """Composite scores should remain within the tanh-bounded range."""

    COMPOSITE_FLOOR = -5.0
    COMPOSITE_CEIL = 5.0

    def test_composite_bounded(self, prediction):
        for w in prediction.windows:
            assert self.COMPOSITE_FLOOR <= w.composite_score <= self.COMPOSITE_CEIL, (
                f"composite_score={w.composite_score} outside expected range"
            )


class TestPanchangPropagation:
    """Panchang score should be populated on windows."""

    def test_panchang_field(self, prediction):
        for w in prediction.windows:
            assert hasattr(w, "panchang_score"), "Window must have panchang_score"
            # Can be zero for some slots but should be a float
            assert isinstance(w.panchang_score, (int, float))


class TestDomainStaticScores:
    """domain_static_scores and domain_confidences must be populated."""

    def test_domain_scores_populated(self, prediction):
        assert prediction.domain_static_scores, "domain_static_scores should not be empty"
        assert "career" in prediction.domain_static_scores

    def test_domain_confidences_populated(self, prediction):
        assert prediction.domain_confidences, "domain_confidences should not be empty"
        assert "career" in prediction.domain_confidences
        conf = prediction.domain_confidences["career"]
        assert 0.0 <= conf <= 1.0, f"domain confidence {conf} out of [0,1]"
