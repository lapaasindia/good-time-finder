from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

from app.astrology.calculations import build_context
from app.core.models import (
    AstroContext,
    EventDefinition,
    EventSlice,
    GeoLocation,
    Person,
    RuleResult,
    TimeRange,
)
from app.core.scoring import score_event
from app.rules.registry import RuleRegistry


def generate_slices(time_range: TimeRange) -> list[datetime]:
    out: list[datetime] = []
    cur = time_range.start
    step = timedelta(minutes=time_range.step_minutes)
    while cur <= time_range.end:
        out.append(cur)
        cur += step
    return out


def evaluate_event_at_context(
    event_def: EventDefinition,
    ctx: AstroContext,
    person: Person,
    registry: RuleRegistry,
) -> EventSlice | None:
    try:
        rule = registry.get(event_def.rule_key)
    except KeyError:
        return None

    result: RuleResult = rule.evaluate(ctx, person)

    if not result.occurring:
        return None

    nature = result.nature_override or event_def.nature
    description = result.description_override or event_def.description
    score = score_event(nature, result.weight)

    return EventSlice(
        event_name=event_def.name,
        nature=nature,
        description=description,
        time=ctx.dt,
        score=score,
    )


class GoodTimeEngine:
    def __init__(
        self,
        registry: RuleRegistry,
        max_workers: int = 4,
    ) -> None:
        self.registry = registry
        self.max_workers = max_workers

    def _build_contexts(
        self,
        time_points: list[datetime],
        location: GeoLocation,
        person: Person,
    ) -> list[AstroContext]:
        contexts = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {
                ex.submit(build_context, dt, location, person): dt
                for dt in time_points
            }
            results: dict[datetime, AstroContext] = {}
            for future in as_completed(futures):
                dt = futures[future]
                try:
                    results[dt] = future.result()
                except Exception as exc:
                    raise RuntimeError(
                        f"Failed to build astro context for {dt}: {exc}"
                    ) from exc
        contexts = [results[dt] for dt in time_points]
        return contexts

    def evaluate_range(
        self,
        person: Person,
        location: GeoLocation,
        time_range: TimeRange,
        event_defs: list[EventDefinition],
    ) -> dict[str, list[EventSlice]]:
        time_points = generate_slices(time_range)
        contexts = self._build_contexts(time_points, location, person)

        by_event: dict[str, list[EventSlice]] = {e.name: [] for e in event_defs}

        for ctx in contexts:
            for event_def in event_defs:
                hit = evaluate_event_at_context(
                    event_def, ctx, person, self.registry
                )
                if hit:
                    by_event[event_def.name].append(hit)

        return by_event
