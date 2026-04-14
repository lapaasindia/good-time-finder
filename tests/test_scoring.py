import math

from app.core.enums import EventNature
from app.core.scoring import rank_window, score_event


def test_good_event_positive_score():
    assert score_event(EventNature.GOOD) == 3.0


def test_bad_event_negative_score():
    assert score_event(EventNature.BAD) == -3.0


def test_neutral_event_zero_score():
    assert score_event(EventNature.NEUTRAL) == 0.0


def test_weight_applied():
    assert score_event(EventNature.GOOD, weight=2.0) == 6.0


def test_rank_window_longer_is_higher():
    rank_short = rank_window(3.0, 30)
    rank_long = rank_window(3.0, 120)
    assert rank_long > rank_short


def test_rank_window_higher_score_is_higher():
    rank_low = rank_window(1.0, 60)
    rank_high = rank_window(3.0, 60)
    assert rank_high > rank_low


def test_rank_window_zero_duration():
    assert rank_window(3.0, 0) == 0.0


def test_rank_window_negative_score():
    rank = rank_window(-3.0, 60)
    assert rank < 0
