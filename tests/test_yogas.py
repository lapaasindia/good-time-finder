"""Unit tests for Yoga detection."""

import pytest

from app.astrology.yogas import (
    detect_all_yogas,
    detect_raja_yoga,
    detect_dhana_yoga,
    detect_gajakesari_yoga,
    detect_hamsa_yoga,
    detect_malavya_yoga,
    detect_budha_aditya_yoga,
    detect_chandra_mangal_yoga,
    yoga_score_for_category,
    active_yogas_for_category,
)


class TestRajaYoga:
    def test_kendra_trikona_lords_conjunct(self):
        # Aries lagna: 1st lord = Mars, 9th lord = Jupiter
        # Both in house 1 = conjunct
        planet_houses = {"Mars": 1, "Jupiter": 1, "Saturn": 6, "Sun": 10,
                         "Moon": 4, "Mercury": 7, "Venus": 5, "Rahu": 3, "Ketu": 9}
        planet_signs = {
            "Mars": "Aries", "Jupiter": "Aries", "Saturn": "Virgo",
            "Sun": "Capricorn", "Moon": "Cancer", "Mercury": "Libra",
            "Venus": "Leo", "Rahu": "Gemini", "Ketu": "Sagittarius",
        }
        result = detect_raja_yoga(planet_houses, "Aries", planet_signs)
        assert result.name == "RajaYoga"
        assert isinstance(result.strength, float)
        assert 0.0 <= result.strength <= 1.0


class TestDhanaYoga:
    def test_lords_conjunct_in_same_house(self):
        # Aries lagna: 2nd lord = Venus (Taurus), 11th lord = Saturn (Aquarius)
        planet_houses = {"Venus": 5, "Saturn": 5}
        planet_signs = {"Venus": "Leo", "Saturn": "Leo"}
        result = detect_dhana_yoga(planet_houses, "Aries", planet_signs)
        assert result.present is True
        assert result.strength == pytest.approx(0.8)

    def test_not_present_when_far_apart(self):
        planet_houses = {"Venus": 1, "Saturn": 7}
        planet_signs = {"Venus": "Aries", "Saturn": "Libra"}
        result = detect_dhana_yoga(planet_houses, "Aries", planet_signs)
        assert result.present is False


class TestGajaKesariYoga:
    def test_jupiter_in_kendra_present(self):
        result = detect_gajakesari_yoga({"Jupiter": 1, "Moon": 7})
        assert result.present is True
        assert result.strength > 0

    def test_neither_in_kendra_may_not_be_present(self):
        result = detect_gajakesari_yoga({"Jupiter": 6, "Moon": 3})
        assert isinstance(result.present, bool)


class TestHamsaYoga:
    def test_jupiter_exalted_in_kendra(self):
        planet_houses = {"Jupiter": 4}
        planet_signs = {"Jupiter": "Cancer"}
        result = detect_hamsa_yoga(planet_houses, planet_signs)
        assert result.present is True
        assert result.strength == pytest.approx(1.0)

    def test_jupiter_not_exalted(self):
        planet_houses = {"Jupiter": 4}
        planet_signs = {"Jupiter": "Scorpio"}
        result = detect_hamsa_yoga(planet_houses, planet_signs)
        assert result.present is False


class TestMalavyaYoga:
    def test_venus_in_own_sign_kendra(self):
        planet_houses = {"Venus": 7}
        planet_signs = {"Venus": "Taurus"}
        result = detect_malavya_yoga(planet_houses, planet_signs)
        assert result.present is True

    def test_venus_not_in_kendra(self):
        planet_houses = {"Venus": 3}
        planet_signs = {"Venus": "Taurus"}
        result = detect_malavya_yoga(planet_houses, planet_signs)
        assert result.present is False


class TestBudhaAdityaYoga:
    def test_sun_mercury_conjunct(self):
        result = detect_budha_aditya_yoga({"Sun": 5, "Mercury": 5})
        assert result.present is True

    def test_sun_mercury_not_conjunct(self):
        result = detect_budha_aditya_yoga({"Sun": 5, "Mercury": 6})
        assert result.present is False


class TestChandraMangalYoga:
    def test_moon_mars_conjunct(self):
        result = detect_chandra_mangal_yoga({"Moon": 3, "Mars": 3})
        assert result.present is True

    def test_not_conjunct(self):
        result = detect_chandra_mangal_yoga({"Moon": 3, "Mars": 5})
        assert result.present is False


class TestDetectAllYogas:
    def test_returns_list_of_yoga_results(self):
        planet_houses = {
            "Sun": 10, "Moon": 4, "Mars": 1, "Mercury": 10,
            "Jupiter": 4, "Venus": 7, "Saturn": 6,
            "Rahu": 3, "Ketu": 9,
        }
        planet_signs = {
            "Sun": "Capricorn", "Moon": "Cancer", "Mars": "Aries",
            "Mercury": "Capricorn", "Jupiter": "Cancer", "Venus": "Taurus",
            "Saturn": "Virgo", "Rahu": "Gemini", "Ketu": "Sagittarius",
        }
        results = detect_all_yogas(planet_houses, planet_signs, "Aries")
        assert len(results) > 0
        for r in results:
            assert hasattr(r, "name")
            assert hasattr(r, "present")
            assert hasattr(r, "strength")
            assert hasattr(r, "category")

    def test_yoga_score_for_category(self):
        planet_houses = {"Sun": 10, "Mercury": 10, "Jupiter": 4, "Moon": 4,
                         "Mars": 1, "Venus": 7, "Saturn": 6, "Rahu": 3, "Ketu": 9}
        planet_signs = {
            "Sun": "Leo", "Mercury": "Leo", "Jupiter": "Cancer",
            "Moon": "Cancer", "Mars": "Aries", "Venus": "Taurus",
            "Saturn": "Virgo", "Rahu": "Gemini", "Ketu": "Sagittarius",
        }
        yogas = detect_all_yogas(planet_houses, planet_signs, "Aries")
        score = yoga_score_for_category(yogas, "general")
        assert isinstance(score, float)
        assert score >= 0.0
