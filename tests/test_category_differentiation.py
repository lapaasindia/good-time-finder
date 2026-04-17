"""Phase 3: Verify category differentiation (different weights per category)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.core.models import GeoLocation, Person, TimeRange
from app.services.life_predictor import LifePredictorService
from app.core.ranking import CATEGORY_WEIGHTS

@pytest.fixture
def predictor():
    return LifePredictorService()


@pytest.fixture
def person():
    return Person(
        name="CatDiff",
        birth_datetime=datetime(1990, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        birth_location=GeoLocation(latitude=28.6, longitude=77.2, timezone="Asia/Kolkata"),
    )


@pytest.fixture
def location():
    return GeoLocation(latitude=28.6, longitude=77.2, timezone="Asia/Kolkata")


def test_category_weights_are_unique():
    """All 15 categories should have distinct weight profiles."""
    weights_seen = set()
    for cat, w in CATEGORY_WEIGHTS.items():
        w_tuple = (
            w.rule, w.shadbala, w.gochara, w.dasha, w.yoga, w.ashtakavarga,
            w.panchang, w.tara, w.chandra_bala, w.avastha, w.pushkara,
            w.sudarshana, w.jaimini, w.arudha, w.gulika, w.badhaka,
            w.bhrigu, w.kp, w.kp_cuspal, w.double_transit,
            w.gochara_house_specific, w.planet_focus
        )
        weights_seen.add(w_tuple)
    
    assert len(weights_seen) == len(CATEGORY_WEIGHTS), "Some categories share identical weights!"


def test_category_composites_differ(predictor, person, location):
    """The same chart should produce different composite scores for different categories."""
    time_range = TimeRange(
        start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        step_minutes=720,
    )
    
    cats_to_test = ["career", "marriage", "health", "finance", "education"]
    scores = {}
    
    for cat in cats_to_test:
        res = predictor.predict(person, location, time_range, cat)
        scores[cat] = res.overall_period_score
        
    distinct_scores = set(scores.values())
    assert len(distinct_scores) > 1, f"Categories produced identical scores: {scores}"
