"""Unit tests for Gochara transit scoring."""

import pytest

from app.astrology.gochara import (
    gochara_score,
    total_gochara_score,
    category_gochara_score,
    GOOD_HOUSES_FROM_NATAL_MOON,
    BAD_HOUSES_FROM_NATAL_MOON,
)


class TestGocharaScore:
    def test_jupiter_in_good_house_positive(self):
        # Jupiter good in house 2 from natal Moon
        # natal Moon = Aries (index 0), house 2 = Taurus
        planet_signs = {"Jupiter": "Taurus"}
        scores = gochara_score(planet_signs, "Aries")
        assert scores["Jupiter"] > 0

    def test_saturn_in_bad_house_negative(self):
        # Saturn bad in house 1 from natal Moon
        # natal Moon = Aries, house 1 = Aries
        planet_signs = {"Saturn": "Aries"}
        scores = gochara_score(planet_signs, "Aries")
        assert scores["Saturn"] < 0

    def test_sun_in_bad_house_negative(self):
        # Sun bad houses from natal Moon include house 2
        # natal Moon = Aries (index 0), house 2 = Taurus
        planet_signs = {"Sun": "Taurus"}
        scores = gochara_score(planet_signs, "Aries")
        assert scores["Sun"] < 0.0

    def test_sun_in_good_house_positive(self):
        # Sun good houses: {3, 6, 10, 11}
        # natal Moon = Aries, house 3 = Gemini
        planet_signs = {"Sun": "Gemini"}
        scores = gochara_score(planet_signs, "Aries")
        assert scores["Sun"] > 0.0

    def test_all_planets_have_scores(self):
        planet_signs = {
            "Sun": "Aries", "Moon": "Taurus", "Mars": "Gemini",
            "Mercury": "Cancer", "Jupiter": "Leo", "Venus": "Virgo",
            "Saturn": "Libra", "Rahu": "Scorpio",
        }
        scores = gochara_score(planet_signs, "Aries")
        assert len(scores) == len(planet_signs)

    def test_invalid_sign_returns_zero(self):
        scores = gochara_score({"Jupiter": "Invalid"}, "Aries")
        assert scores["Jupiter"] == 0.0


class TestTotalGocharaScore:
    def test_returns_float(self):
        planet_signs = {"Jupiter": "Leo", "Saturn": "Aries"}
        result = total_gochara_score(planet_signs, "Aries")
        assert isinstance(result, float)

    def test_empty_returns_zero(self):
        result = total_gochara_score({}, "Aries")
        assert result == 0.0


class TestCategoryGocharaScore:
    def test_filters_to_relevant_planets(self):
        planet_signs = {
            "Jupiter": "Leo",   # house 5 from Aries — good for Jupiter
            "Saturn": "Aries",  # house 1 from Aries — bad for Saturn
        }
        # Only Jupiter relevant
        score_jupiter_only = category_gochara_score(planet_signs, "Aries", {"Jupiter"})
        # Both relevant
        score_both = category_gochara_score(planet_signs, "Aries", {"Jupiter", "Saturn"})
        assert score_jupiter_only != score_both

    def test_empty_relevant_returns_zero(self):
        planet_signs = {"Jupiter": "Leo"}
        assert category_gochara_score(planet_signs, "Aries", set()) == 0.0
