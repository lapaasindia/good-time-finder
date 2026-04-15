"""Unit tests for per-category ranking model."""

import pytest

from app.core.ranking import (
    compute_composite_score,
    get_weights,
    rank_window,
    CATEGORY_WEIGHTS,
)


class TestGetWeights:
    def test_known_category_returns_correct_weights(self):
        w = get_weights("career")
        assert w.dasha == 1.5
        assert w.rule == 0.5

    def test_unknown_category_returns_defaults(self):
        w = get_weights("unknown_category")
        assert w.rule == 1.0
        assert w.dasha == 1.2

    def test_all_categories_present(self):
        for cat in ["career", "finance", "health", "marriage", "travel",
                    "education", "property", "children", "spirituality", "legal", "general"]:
            w = get_weights(cat)
            assert w.rule > 0


class TestCompositeScore:
    def test_zero_inputs_returns_zero(self):
        score = compute_composite_score("career", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        assert score == pytest.approx(0.0)

    def test_positive_rule_score_gives_positive_composite(self):
        score = compute_composite_score("career", rule_score=3.0)
        assert score > 0

    def test_negative_rule_score_gives_negative_composite(self):
        score = compute_composite_score("travel", rule_score=-3.0)
        assert score < 0

    def test_dasha_bonus_weighted_heavily_for_career(self):
        score_with_dasha = compute_composite_score("career", rule_score=1.0, dasha_bonus=2.0)
        score_without = compute_composite_score("career", rule_score=1.0, dasha_bonus=0.0)
        assert score_with_dasha > score_without

    def test_yoga_weighted_for_spirituality(self):
        score_with_yoga = compute_composite_score("spirituality", rule_score=1.0, yoga_score=1.0)
        score_without = compute_composite_score("spirituality", rule_score=1.0, yoga_score=0.0)
        assert score_with_yoga > score_without

    def test_categories_differ_for_same_inputs(self):
        score_career = compute_composite_score("career", rule_score=1.0, dasha_bonus=2.0)
        score_travel = compute_composite_score("travel", rule_score=1.0, dasha_bonus=2.0)
        assert score_career != score_travel


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
