from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime

from app.config import load_event_catalog
from app.core.engine import GoodTimeEngine
from app.core.enums import EventNature, EventTag
from app.core.models import EventDefinition, GeoLocation, Person, TimeRange, TimeWindow
from app.core.scoring import rank_window
from app.core.windows import merge_slices_to_windows
from app.rules.registry import build_default_registry


@dataclass
class CombinedWindow:
    start: datetime
    end: datetime
    total_score: float
    rank: float
    active_events: list[str] = field(default_factory=list)

    @property
    def duration_minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60


@dataclass
class FinderResult:
    windows: list[TimeWindow]
    combined_windows: list[CombinedWindow]


class GoodTimeFinderService:
    def __init__(self) -> None:
        self._registry = build_default_registry()
        self._catalog = load_event_catalog()
        self._engine = GoodTimeEngine(registry=self._registry)

    def find(
        self,
        person: Person,
        location: GeoLocation,
        time_range: TimeRange,
        selected_tags: list[EventTag],
    ) -> FinderResult:
        selected_events = [
            e for e in self._catalog
            if any(tag in e.tags for tag in selected_tags)
        ]

        if not selected_events:
            return FinderResult(windows=[], combined_windows=[])

        by_event = self._engine.evaluate_range(
            person=person,
            location=location,
            time_range=time_range,
            event_defs=selected_events,
        )

        all_windows: list[TimeWindow] = []
        for event_def in selected_events:
            all_windows.extend(
                merge_slices_to_windows(
                    event_def=event_def,
                    slices=by_event[event_def.name],
                    step_minutes=time_range.step_minutes,
                )
            )

        all_windows.sort(key=lambda w: (w.start, -w.score))

        combined = self._build_combined_windows(all_windows, time_range.step_minutes)

        return FinderResult(windows=all_windows, combined_windows=combined)

    def _build_combined_windows(
        self,
        windows: list[TimeWindow],
        step_minutes: int,
    ) -> list[CombinedWindow]:
        if not windows:
            return []

        from collections import defaultdict
        from datetime import timedelta

        score_map: dict[datetime, float] = defaultdict(float)
        events_map: dict[datetime, list[str]] = defaultdict(list)

        for w in windows:
            cur = w.start
            while cur < w.end:
                score_map[cur] += w.score
                events_map[cur].append(w.event_name)
                cur += timedelta(minutes=step_minutes)

        sorted_times = sorted(score_map.keys())
        if not sorted_times:
            return []

        step = timedelta(minutes=step_minutes)
        combined: list[CombinedWindow] = []

        start = sorted_times[0]
        prev = sorted_times[0]
        scores_in_window = [score_map[sorted_times[0]]]
        events_in_window: set[str] = set(events_map[sorted_times[0]])

        for t in sorted_times[1:]:
            if t - prev <= step:
                prev = t
                scores_in_window.append(score_map[t])
                events_in_window.update(events_map[t])
            else:
                total = sum(scores_in_window) / len(scores_in_window)
                dur = (prev + step - start).total_seconds() / 60
                combined.append(
                    CombinedWindow(
                        start=start,
                        end=prev + step,
                        total_score=total,
                        rank=rank_window(total, dur),
                        active_events=sorted(events_in_window),
                    )
                )
                start = t
                prev = t
                scores_in_window = [score_map[t]]
                events_in_window = set(events_map[t])

        total = sum(scores_in_window) / len(scores_in_window)
        dur = (prev + step - start).total_seconds() / 60
        combined.append(
            CombinedWindow(
                start=start,
                end=prev + step,
                total_score=total,
                rank=rank_window(total, dur),
                active_events=sorted(events_in_window),
            )
        )

        combined.sort(key=lambda c: -c.rank)
        return combined
