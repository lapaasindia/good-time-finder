from datetime import datetime, timedelta, timezone

import pytest

from app.core.enums import EventNature, EventTag
from app.core.models import EventDefinition, EventSlice
from app.core.windows import merge_slices_to_windows

_DEF = EventDefinition(
    name="TestEvent",
    nature=EventNature.GOOD,
    description="Test event",
    tags=[EventTag.TRAVEL],
    rule_key="test_rule",
)
_BASE = datetime(2026, 4, 12, 10, 0, tzinfo=timezone.utc)
_STEP = 15


def _slice(offset_minutes: int) -> EventSlice:
    return EventSlice(
        event_name="TestEvent",
        nature=EventNature.GOOD,
        description="Test event",
        time=_BASE + timedelta(minutes=offset_minutes),
        score=3.0,
    )


def test_empty_slices_returns_empty():
    assert merge_slices_to_windows(_DEF, [], _STEP) == []


def test_single_slice_creates_one_window():
    windows = merge_slices_to_windows(_DEF, [_slice(0)], _STEP)
    assert len(windows) == 1
    assert windows[0].start == _BASE
    assert windows[0].end == _BASE + timedelta(minutes=15)


def test_contiguous_slices_merge_into_one_window():
    slices = [_slice(0), _slice(15), _slice(30)]
    windows = merge_slices_to_windows(_DEF, slices, _STEP)
    assert len(windows) == 1
    assert windows[0].start == _BASE
    assert windows[0].end == _BASE + timedelta(minutes=45)


def test_gap_creates_two_windows():
    slices = [_slice(0), _slice(15), _slice(60), _slice(75)]
    windows = merge_slices_to_windows(_DEF, slices, _STEP)
    assert len(windows) == 2
    assert windows[0].start == _BASE
    assert windows[0].end == _BASE + timedelta(minutes=30)
    assert windows[1].start == _BASE + timedelta(minutes=60)
    assert windows[1].end == _BASE + timedelta(minutes=90)


def test_average_score_computed():
    slices = [
        EventSlice(event_name="T", nature=EventNature.GOOD, description="", time=_BASE, score=3.0),
        EventSlice(event_name="T", nature=EventNature.GOOD, description="", time=_BASE + timedelta(minutes=15), score=6.0),
    ]
    windows = merge_slices_to_windows(_DEF, slices, _STEP)
    assert windows[0].score == pytest.approx(4.5)


def test_window_tags_match_event_def():
    windows = merge_slices_to_windows(_DEF, [_slice(0)], _STEP)
    assert EventTag.TRAVEL in windows[0].tags
