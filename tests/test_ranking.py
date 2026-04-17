"""Unit tests for the current ranking model."""

import math

import pytest

from app.core.ranking import (
    CATEGORY_WEIGHTS,
    USE_ML_MODEL,
    batch_composite_scores,
    compute_composite_score,
    get_weights,
    rank_window,
)


class TestGetWeights:
    def test_known_category_returns_current_tuned_weights(self):
        # We know career is populated. Ensure it matches current baseline 
        w = get_weights("career")
        assert w.rule == pytest.approx(1.26)
        assert w.dasha == pytest.approx(1.40)
        assert w.kp_cuspal == pytest.approx(1.0)

    def test_unknown_category_returns_defaults(self):
        w = get_weights("unknown_category")
        assert w.rule == 1.0
        assert w.dasha == 1.0

    def test_known_categories_use_tuned_table(self):
        tuned = get_weights("career")
        default = get_weights("unknown_category")
        assert tuned != default
        assert len(CATEGORY_WEIGHTS) >= 10


class TestCompositeScore:
    def test_zero_inputs_return_finite_calibrated_score(self):
        score = compute_composite_score("career", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        assert math.isfinite(float(score))
        assert -3.0 <= float(score) <= 3.0

    def test_general_category_keeps_explicit_offset(self):
        general_score = compute_composite_score("general", rule_score=0.0)
        career_score = compute_composite_score("career", rule_score=0.0)
        assert general_score == pytest.approx(career_score + 1.0, abs=1e-6)

    def test_batch_scores_match_single_item_scores(self):
        row = [1.0, 0.0, 0.0, 2.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        batch_score = batch_composite_scores("career", [row])[0]
        single_score = compute_composite_score(
            "career",
            rule_score=1.0,
            dasha_bonus=2.0,
            yoga_score=0.5,
        )
        assert batch_score == pytest.approx(single_score, abs=1e-6)

    def test_spirituality_yoga_signal_changes_score(self):
        score_with_yoga = compute_composite_score("spirituality", rule_score=1.0, yoga_score=1.0)
        score_without = compute_composite_score("spirituality", rule_score=1.0, yoga_score=0.0)
        if USE_ML_MODEL:
            assert score_with_yoga != pytest.approx(score_without, abs=1e-6)
        else:
            assert score_with_yoga > score_without

    def test_negative_inputs_are_still_valid_scores(self):
        score = compute_composite_score("travel", rule_score=-3.0)
        assert math.isfinite(float(score))
        # It returns raw score now, but we check if it works


class TestRankWindow:
    def test_zero_duration_returns_zero(self):
        assert rank_window(3.0, 0) == 0.0

    def test_longer_duration_higher_rank(self):
        r1 = rank_window(3.0, 30)
        r2 = rank_window(3.0, 120)
        assert r2 > r1

    def test_higher_score_higher_rank(self):
        r1 = rank_window(1.0, 60)
        r2 = rank_window(5.0, 60)
        assert r2 > r1

    def test_negative_score_gives_negative_rank(self):
        assert rank_window(-3.0, 60) < 0
