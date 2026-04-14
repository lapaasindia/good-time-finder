from __future__ import annotations

from datetime import timedelta

from app.core.models import EventDefinition, EventSlice, TimeWindow


def merge_slices_to_windows(
    event_def: EventDefinition,
    slices: list[EventSlice],
    step_minutes: int,
) -> list[TimeWindow]:
    if not slices:
        return []

    slices = sorted(slices, key=lambda x: x.time)
    step = timedelta(minutes=step_minutes)
    windows: list[TimeWindow] = []

    start = slices[0].time
    prev = slices[0].time
    scores = [slices[0].score]

    for s in slices[1:]:
        if s.time - prev <= step:
            prev = s.time
            scores.append(s.score)
            continue

        windows.append(
            TimeWindow(
                event_name=event_def.name,
                start=start,
                end=prev + step,
                nature=event_def.nature,
                description=event_def.description,
                score=sum(scores) / len(scores),
                tags=list(event_def.tags),
            )
        )
        start = s.time
        prev = s.time
        scores = [s.score]

    windows.append(
        TimeWindow(
            event_name=event_def.name,
            start=start,
            end=prev + step,
            nature=event_def.nature,
            description=event_def.description,
            score=sum(scores) / len(scores),
            tags=list(event_def.tags),
        )
    )
    return windows
