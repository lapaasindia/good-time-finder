"""Phase 2: Verify KP scores vary per time slot (not frozen to natal values)."""
from __future__ import annotations

import statistics
from datetime import datetime, timezone

import pytest

from app.core.models import GeoLocation, Person, TimeRange
from app.services.life_predictor import LifePredictorService


@pytest.fixture
def predictor():
    return LifePredictorService()


@pytest.fixture
def person():
    return Person(
        name="KPDyn",
        birth_datetime=datetime(1990, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        birth_location=GeoLocation(latitude=28.6, longitude=77.2, timezone="Asia/Kolkata"),
    )


@pytest.fixture
def location():
    return GeoLocation(latitude=28.6, longitude=77.2, timezone="Asia/Kolkata")


def test_kp_cuspal_varies_across_slots(predictor, person, location):
    """KP cuspal should rotate across a 1-month window with 4-hour steps."""
    time_range = TimeRange(
        start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end=datetime(2025, 1, 10, tzinfo=timezone.utc),
        step_minutes=240,
    )
    result = predictor.predict(person, location, time_range, "career")

    kp_cuspals = [w.kp_cuspal_score for w in result.windows]
    assert len(kp_cuspals) >= 5, "need multiple windows to measure variance"

    distinct = set(round(v, 2) for v in kp_cuspals)
    assert len(distinct) >= 2, (
        f"kp_cuspal_score is frozen across slots: only {distinct}"
    )


def test_kp_score_varies_across_slots(predictor, person, location):
    """KP score based on transit Moon sub-lord should change (Moon moves ~13°/day)."""
    time_range = TimeRange(
        start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end=datetime(2025, 1, 10, tzinfo=timezone.utc),
        step_minutes=240,
    )
    result = predictor.predict(person, location, time_range, "career")

    kp_scores = [w.kp_score for w in result.windows]
    distinct = set(round(v, 2) for v in kp_scores)
    # Moon sub-lord changes on order of hours, so 10 days should see multiple distinct values
    assert len(distinct) >= 2, f"kp_score frozen: only {distinct}"


def test_natal_kp_anchors_preserved(predictor, person, location):
    """kp_natal_score and kp_natal_cuspal should be populated separately from dynamic values."""
    time_range = TimeRange(
        start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end=datetime(2025, 1, 3, tzinfo=timezone.utc),
        step_minutes=720,
    )
    result = predictor.predict(person, location, time_range, "career")

    # natal anchors exist as distinct fields
    assert hasattr(result, "kp_natal_score")
    assert hasattr(result, "kp_natal_cuspal")
    # They should be floats (not None)
    assert isinstance(result.kp_natal_score, (int, float))
    assert isinstance(result.kp_natal_cuspal, (int, float))
