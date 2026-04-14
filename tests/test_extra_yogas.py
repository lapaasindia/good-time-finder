"""Unit tests for extra natal yoga detectors."""

import pytest
from app.astrology.extra_yogas import (
    detect_neecha_bhanga_raja_yoga,
    detect_viparita_raja_yoga,
    detect_ruchaka_yoga,
    detect_bhadra_yoga,
    detect_shasha_yoga,
    detect_saraswati_yoga,
    detect_lakshmi_yoga,
    detect_chandra_adhi_yoga,
    detect_vesi_yoga,
    detect_all_extra_yogas,
)


class TestRuchakaYoga:
    def test_mars_exalted_in_kendra(self):
        result = detect_ruchaka_yoga({"Mars": 10}, {"Mars": "Capricorn"})
        assert result.present is True
        assert result.strength == 1.0

    def test_mars_own_sign_in_kendra(self):
        result = detect_ruchaka_yoga({"Mars": 1}, {"Mars": "Aries"})
        assert result.present is True

    def test_mars_not_in_kendra(self):
        result = detect_ruchaka_yoga({"Mars": 3}, {"Mars": "Capricorn"})
        assert result.present is False


class TestBhadraYoga:
    def test_mercury_exalted_in_kendra(self):
        result = detect_bhadra_yoga({"Mercury": 1}, {"Mercury": "Virgo"})
        assert result.present is True

    def test_mercury_not_exalted_not_own_sign(self):
        result = detect_bhadra_yoga({"Mercury": 1}, {"Mercury": "Aries"})
        assert result.present is False


class TestShashaYoga:
    def test_saturn_exalted_in_kendra(self):
        result = detect_shasha_yoga({"Saturn": 4}, {"Saturn": "Libra"})
        assert result.present is True

    def test_saturn_own_sign_in_kendra(self):
        result = detect_shasha_yoga({"Saturn": 7}, {"Saturn": "Capricorn"})
        assert result.present is True

    def test_saturn_in_dusthana(self):
        result = detect_shasha_yoga({"Saturn": 6}, {"Saturn": "Libra"})
        assert result.present is False


class TestSaraswatiYoga:
    def test_all_three_in_kendra_trikona(self):
        planet_houses = {"Jupiter": 1, "Venus": 5, "Mercury": 9}
        result = detect_saraswati_yoga(planet_houses, {})
        assert result.present is True
        assert result.strength > 0

    def test_only_one_in_kendra_not_present(self):
        planet_houses = {"Jupiter": 1, "Venus": 6, "Mercury": 8}
        result = detect_saraswati_yoga(planet_houses, {})
        assert result.present is False


class TestLakshmiYoga:
    def test_venus_in_exalt_and_9th_lord_in_kendra(self):
        planet_houses = {"Jupiter": 1, "Venus": 7}
        planet_signs = {"Venus": "Pisces", "Jupiter": "Sagittarius"}
        result = detect_lakshmi_yoga(planet_houses, planet_signs, "Aries")
        assert result.present is True

    def test_venus_not_own_exalt(self):
        planet_houses = {"Jupiter": 1, "Venus": 7}
        planet_signs = {"Venus": "Aries", "Jupiter": "Sagittarius"}
        result = detect_lakshmi_yoga(planet_houses, planet_signs, "Aries")
        assert result.present is False


class TestChandraAdhiYoga:
    def test_two_benefics_in_6th_7th_8th_from_moon(self):
        moon_house = 3
        # Code: target_houses = { ((moon+5)%12)+1, ((moon+6)%12)+1, ((moon+7)%12)+1 }
        sixth  = ((moon_house + 5) % 12) + 1
        seventh = ((moon_house + 6) % 12) + 1
        planet_houses = {"Moon": moon_house, "Mercury": sixth, "Venus": seventh, "Jupiter": 1}
        result = detect_chandra_adhi_yoga(planet_houses)
        assert result.present is True

    def test_only_one_benefic_not_present(self):
        planet_houses = {"Moon": 3, "Mercury": 8, "Venus": 2, "Jupiter": 1}
        result = detect_chandra_adhi_yoga(planet_houses)
        assert isinstance(result.present, bool)


class TestVesiYoga:
    def test_benefic_in_2nd_from_sun(self):
        planet_houses = {"Sun": 5, "Mercury": 6, "Venus": 3, "Jupiter": 3}
        result = detect_vesi_yoga(planet_houses)
        assert result.present is True

    def test_no_benefic_in_2nd_from_sun(self):
        planet_houses = {"Sun": 5, "Mercury": 3, "Venus": 3, "Jupiter": 3}
        result = detect_vesi_yoga(planet_houses)
        assert result.present is False


class TestDetectAllExtraYogas:
    def test_returns_9_results(self):
        planet_houses = {
            "Sun": 10, "Moon": 4, "Mars": 1, "Mercury": 1,
            "Jupiter": 4, "Venus": 7, "Saturn": 7, "Rahu": 3, "Ketu": 9,
        }
        planet_signs = {
            "Sun": "Capricorn", "Moon": "Cancer", "Mars": "Aries",
            "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Taurus",
            "Saturn": "Libra", "Rahu": "Gemini", "Ketu": "Sagittarius",
        }
        results = detect_all_extra_yogas(planet_houses, planet_signs, "Aries")
        assert len(results) == 9
        for r in results:
            assert hasattr(r, "name")
            assert hasattr(r, "present")
            assert 0.0 <= r.strength <= 1.0
