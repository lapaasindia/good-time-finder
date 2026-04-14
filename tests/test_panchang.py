"""Unit tests for Panchang (Yoga + Karana)."""

import pytest
from app.astrology.panchang import (
    compute_yoga,
    compute_karana,
    build_panchang,
    YOGA_NAMES,
    YOGA_NATURE,
    KARANA_NATURE,
)


class TestComputeYoga:
    def test_returns_valid_yoga_name(self):
        from datetime import datetime, timezone
        dt = datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)
        name, nature = compute_yoga(dt)
        assert name in YOGA_NAMES
        assert nature in {"good", "bad", "neutral"}

    def test_all_natures_are_valid(self):
        for name, nature in YOGA_NATURE.items():
            assert nature in {"good", "bad"}

    def test_different_times_may_give_different_yogas(self):
        from datetime import datetime, timezone
        dt1 = datetime(2025, 6, 1, 0, 0, tzinfo=timezone.utc)
        dt2 = datetime(2025, 6, 15, 0, 0, tzinfo=timezone.utc)
        name1, _ = compute_yoga(dt1)
        name2, _ = compute_yoga(dt2)
        assert name1 in YOGA_NAMES
        assert name2 in YOGA_NAMES


class TestComputeKarana:
    def test_returns_valid_karana_name(self):
        from datetime import datetime, timezone
        dt = datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)
        name, nature = compute_karana(dt)
        assert name in KARANA_NATURE
        assert nature in {"good", "bad", "neutral"}

    def test_vishti_is_bad(self):
        assert KARANA_NATURE["Vishti"] == "bad"

    def test_bava_is_good(self):
        assert KARANA_NATURE["Bava"] == "good"


class TestBuildPanchang:
    def test_returns_panchang_data(self):
        from datetime import datetime, timezone
        dt = datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)
        p = build_panchang(dt, "Rohini", 5, "Sunday")
        assert p.nakshatra == "Rohini"
        assert p.tithi == 5
        assert p.weekday == "Sunday"
        assert p.yoga_name in YOGA_NAMES
        assert p.yoga_score in {1.0, -1.0, 0.0}
        assert p.karana_score in {0.5, -0.5, 0.0}

    def test_is_auspicious_reflects_yoga_karana(self):
        from datetime import datetime, timezone
        dt = datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc)
        p = build_panchang(dt, "Rohini", 5, "Sunday")
        if p.yoga_nature == "good" and p.karana_nature != "bad":
            assert p.is_auspicious()
        elif p.yoga_nature == "bad":
            assert not p.is_auspicious()
