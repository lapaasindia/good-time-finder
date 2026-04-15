"""Unit tests for Vimshottari Dasha calculations."""

from datetime import datetime, timezone

import pytest

from app.astrology.dasha import (
    DASHA_ORDER,
    DASHA_YEARS,
    NAKSHATRA_LORD,
    TOTAL_YEARS,
    compute_antardashas,
    compute_mahadashas,
    dasha_bonus_for_category,
    get_active_dasha,
    DashaPeriod,
)


_BIRTH = datetime(1992, 8, 14, 4, 50, tzinfo=timezone.utc)
_NAKSHATRA = "Magha"
_MOON_LON = 120.5


class TestComputeMahadashas:
    def test_returns_nine_periods(self):
        periods = compute_mahadashas(_BIRTH, _NAKSHATRA, _MOON_LON)
        assert len(periods) == 9

    def test_first_period_starts_at_birth(self):
        periods = compute_mahadashas(_BIRTH, _NAKSHATRA, _MOON_LON)
        assert periods[0].start == _BIRTH

    def test_periods_are_contiguous(self):
        periods = compute_mahadashas(_BIRTH, _NAKSHATRA, _MOON_LON)
        for i in range(len(periods) - 1):
            diff = abs((periods[i + 1].start - periods[i].end).total_seconds())
            assert diff < 86400, f"Gap too large between period {i} and {i+1}"

    def test_total_duration_approximately_120_years(self):
        periods = compute_mahadashas(_BIRTH, _NAKSHATRA, _MOON_LON)
        total_days = sum(p.duration_days for p in periods)
        expected = TOTAL_YEARS * 365.25
        assert abs(total_days - expected) < 200

    def test_level_is_mahadasha(self):
        periods = compute_mahadashas(_BIRTH, _NAKSHATRA, _MOON_LON)
        for p in periods:
            assert p.level == "mahadasha"


class TestComputeAntardashas:
    def test_returns_nine_antardashas(self):
        maha = DashaPeriod(
            planet="Jupiter",
            start=_BIRTH,
            end=_BIRTH.replace(year=_BIRTH.year + 16),
            level="mahadasha",
        )
        antardashas = compute_antardashas(maha)
        assert len(antardashas) == 9

    def test_antardashas_are_contiguous(self):
        maha = DashaPeriod(
            planet="Jupiter",
            start=_BIRTH,
            end=_BIRTH.replace(year=_BIRTH.year + 16),
            level="mahadasha",
        )
        antardashas = compute_antardashas(maha)
        for i in range(len(antardashas) - 1):
            diff = abs((antardashas[i + 1].start - antardashas[i].end).total_seconds())
            assert diff < 86400

    def test_level_is_antardasha(self):
        maha = DashaPeriod(
            planet="Jupiter",
            start=_BIRTH,
            end=_BIRTH.replace(year=_BIRTH.year + 16),
            level="mahadasha",
        )
        antardashas = compute_antardashas(maha)
        for a in antardashas:
            assert a.level == "antardasha"
            assert a.parent_planet == "Jupiter"


class TestGetActiveDasha:
    def test_returns_active_period(self):
        periods = compute_mahadashas(_BIRTH, _NAKSHATRA, _MOON_LON)
        query_dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
        maha, antar = get_active_dasha(periods, query_dt)
        assert maha is not None
        assert antar is not None
        assert maha.start <= query_dt < maha.end
        assert antar.start <= query_dt < antar.end

    def test_future_date_out_of_range_returns_none(self):
        periods = compute_mahadashas(_BIRTH, _NAKSHATRA, _MOON_LON)
        query_dt = datetime(2200, 1, 1, tzinfo=timezone.utc)
        maha, antar = get_active_dasha(periods, query_dt)
        assert maha is None


class TestDashaBonus:
    def test_relevant_planet_in_mahadasha_gives_bonus(self):
        maha = DashaPeriod(planet="Jupiter", start=_BIRTH,
                           end=_BIRTH.replace(year=2010), level="mahadasha")
        bonus = dasha_bonus_for_category(maha, None, None, "career")
        assert bonus > 0

    def test_malefic_planet_gives_negative_score(self):
        maha = DashaPeriod(planet="Ketu", start=_BIRTH,
                           end=_BIRTH.replace(year=1999), level="mahadasha")
        bonus = dasha_bonus_for_category(maha, None, None, "finance")
        assert bonus < 0

    def test_none_maha_returns_zero(self):
        assert dasha_bonus_for_category(None, None, None, "career") == 0.0
