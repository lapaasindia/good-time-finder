from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.core.enums import EventNature, EventTag


@dataclass(frozen=True)
class GeoLocation:
    latitude: float
    longitude: float
    timezone: str


@dataclass(frozen=True)
class Person:
    name: str
    birth_datetime: datetime
    birth_location: GeoLocation


@dataclass(frozen=True)
class TimeRange:
    start: datetime
    end: datetime
    step_minutes: int = 15


@dataclass(frozen=True)
class EventDefinition:
    name: str
    nature: EventNature
    description: str
    tags: list[EventTag]
    rule_key: str


@dataclass(frozen=True)
class RuleResult:
    occurring: bool
    nature_override: EventNature | None = None
    description_override: str | None = None
    weight: float = 1.0
    details: dict | None = None


@dataclass(frozen=True)
class EventSlice:
    event_name: str
    nature: EventNature
    description: str
    time: datetime
    score: float


@dataclass(frozen=True)
class TimeWindow:
    event_name: str
    start: datetime
    end: datetime
    nature: EventNature
    description: str
    score: float
    tags: list[EventTag]

    @property
    def duration_minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60


@dataclass
class AstroContext:
    dt: datetime
    location: GeoLocation
    lunar_day: int
    moon_constellation: str
    nakshatra_pada: int
    weekday: str
    lagna: str
    moon_sign: str
    sun_sign: str
    planet_houses: dict[str, int] = field(default_factory=dict)
    planet_signs: dict[str, str] = field(default_factory=dict)
