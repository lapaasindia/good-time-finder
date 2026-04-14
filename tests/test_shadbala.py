"""Unit tests for Shadbala planetary strength calculations."""

import pytest

from app.astrology.shadbala import (
    planet_strength,
    shadbala_summary,
    benefic_strength_score,
    EXALTATION_SIGN,
    DEBILITATION_SIGN,
    OWN_SIGNS,
)


class TestPlanetStrength:
    def test_exalted_planet_has_high_strength(self):
        score = planet_strength("Sun", "Aries", 10)
        assert score > 1.0

    def test_debilitated_planet_has_low_strength(self):
        score = planet_strength("Sun", "Libra", 7)
        exalt_score = planet_strength("Sun", "Aries", 10)
        assert score < exalt_score

    def test_own_sign_is_strong(self):
        score = planet_strength("Moon", "Cancer", 1)
        assert score > 0.8

    def test_score_is_bounded(self):
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            exalt = EXALTATION_SIGN[planet]
            score = planet_strength(planet, exalt, 1)
            assert 0.0 <= score <= 2.0

    def test_all_planets_return_float(self):
        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        for p in planets:
            score = planet_strength(p, "Aries", 5)
            assert isinstance(score, float)


class TestShabdalaSummary:
    def test_returns_dict_with_all_planets(self):
        signs = {
            "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
            "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
            "Saturn": "Libra",
        }
        houses = {p: i + 1 for i, p in enumerate(signs)}
        result = shadbala_summary(signs, houses)
        assert set(result.keys()) == set(signs.keys())
        for v in result.values():
            assert isinstance(v, float)

    def test_exalted_planets_score_higher_than_debilitated(self):
        signs_exalt = {"Sun": "Aries", "Moon": "Taurus"}
        signs_debil = {"Sun": "Libra", "Moon": "Scorpio"}
        houses = {"Sun": 10, "Moon": 4}
        exalt_result = shadbala_summary(signs_exalt, houses)
        debil_result = shadbala_summary(signs_debil, houses)
        assert exalt_result["Sun"] > debil_result["Sun"]
        assert exalt_result["Moon"] > debil_result["Moon"]


class TestBeneficStrengthScore:
    def test_relevant_planets_averaged(self):
        shadbala = {"Jupiter": 1.8, "Venus": 1.2, "Saturn": 0.4}
        score = benefic_strength_score(shadbala, {"Jupiter", "Venus"})
        assert score == pytest.approx(1.5)

    def test_empty_relevant_returns_zero(self):
        assert benefic_strength_score({"Jupiter": 1.5}, set()) == 0.0

    def test_missing_planet_treated_as_zero(self):
        score = benefic_strength_score({"Jupiter": 1.0}, {"Jupiter", "Mars"})
        assert score == pytest.approx(0.5)
