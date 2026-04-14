"""
Life Timeline Generator.

Produces a multi-year narrative timeline of astrologically significant
periods for all life categories, based on:
  - Active Mahadasha / Antardasha
  - Sade Sati phases
  - Jupiter & Saturn transits (key slow-moving planets)
  - Yoga activations

Output: ordered list of LifeEvent dicts with dates, category, intensity, and description.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.astrology.dasha import CATEGORY_PLANETS, compute_mahadashas, get_active_dasha
from app.astrology.sade_sati import compute_sade_sati
from app.astrology.yogas import YogaResult

ALL_CATEGORIES = [
    "career", "finance", "health", "marriage",
    "education", "property", "children", "spirituality", "legal",
]


@dataclass
class LifeEvent:
    start: datetime
    end: datetime
    category: str
    title: str
    description: str
    intensity: str
    score: float
    source: str

    def to_dict(self) -> dict:
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "intensity": self.intensity,
            "score": self.score,
            "source": self.source,
        }


def _dasha_events(
    mahadashas: list,
    range_start: datetime,
    range_end: datetime,
) -> list[LifeEvent]:
    events: list[LifeEvent] = []
    for maha in mahadashas:
        if maha.end < range_start or maha.start > range_end:
            continue
        relevant_cats = [c for c, planets in CATEGORY_PLANETS.items()
                         if maha.planet in planets]
        for cat in relevant_cats:
            events.append(LifeEvent(
                start=max(maha.start, range_start),
                end=min(maha.end, range_end),
                category=cat,
                title=f"{maha.planet} Mahadasha",
                description=(
                    f"{maha.planet} Mahadasha activates {cat}. "
                    f"Duration: {round(maha.duration_days / 365.25, 1)} years."
                ),
                intensity="high",
                score=2.0,
                source="mahadasha",
            ))
    return events


def _sade_sati_events(
    natal_moon_sign: str,
    range_start: datetime,
    range_end: datetime,
) -> list[LifeEvent]:
    result = compute_sade_sati(natal_moon_sign, range_start)
    events: list[LifeEvent] = []

    for phase in result.phases:
        if phase.end < range_start or phase.start > range_end:
            continue
        intensity_map = {"Peak": "very high", "Rising": "moderate", "Setting": "moderate"}
        score_map = {"Peak": -2.0, "Rising": -1.0, "Setting": -0.8}
        events.append(LifeEvent(
            start=max(phase.start, range_start),
            end=min(phase.end, range_end),
            category="general",
            title=f"Sade Sati — {phase.phase} Phase",
            description=(
                f"Saturn transiting {phase.saturn_sign} — {phase.phase} phase of Sade Sati. "
                f"Challenges, restructuring, karmic lessons. Intensity: {phase.intensity}."
            ),
            intensity=intensity_map.get(phase.phase, "moderate"),
            score=score_map.get(phase.phase, -1.0),
            source="sade_sati",
        ))

    if result.dhaiya_active and result.dhaiya_sign:
        events.append(LifeEvent(
            start=range_start,
            end=range_start + timedelta(days=int(2.47 * 365.25)),
            category="general",
            title="Shani Dhaiya Active",
            description=(
                f"Saturn in {result.dhaiya_sign} — Shani Dhaiya (Small Panoti). "
                f"Minor delays and obstacles expected."
            ),
            intensity="mild",
            score=-0.5,
            source="sade_sati",
        ))

    return events


def _yoga_events(
    yogas: list[YogaResult],
    range_start: datetime,
    range_end: datetime,
) -> list[LifeEvent]:
    events: list[LifeEvent] = []
    for yoga in yogas:
        if not yoga.present:
            continue
        events.append(LifeEvent(
            start=range_start,
            end=range_end,
            category=yoga.category,
            title=f"{yoga.name} (Natal Yoga)",
            description=yoga.description,
            intensity="high" if yoga.strength >= 0.8 else "moderate",
            score=yoga.strength,
            source="natal_yoga",
        ))
    return events


def _jupiter_transit_events(
    natal_moon_sign: str,
    range_start: datetime,
    range_end: datetime,
) -> list[LifeEvent]:
    from app.astrology.gochara import GOOD_HOUSES_FROM_NATAL_MOON, BAD_HOUSES_FROM_NATAL_MOON
    from app.core.enums import ZODIAC_SIGNS
    import swisseph as swe

    events: list[LifeEvent] = []
    moon_idx = ZODIAC_SIGNS.index(natal_moon_sign)

    jup_good = GOOD_HOUSES_FROM_NATAL_MOON.get("Jupiter", set())
    jup_bad = BAD_HOUSES_FROM_NATAL_MOON.get("Jupiter", set())

    step = timedelta(days=90)
    dt = range_start
    last_sign = None

    while dt <= range_end:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        utc = dt.astimezone(timezone.utc)
        jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60.0)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        result, _ = swe.calc_ut(jd, swe.JUPITER, flags)
        jup_sign = ZODIAC_SIGNS[int(result[0] / 30) % 12]

        if jup_sign != last_sign:
            jup_idx = ZODIAC_SIGNS.index(jup_sign)
            house = ((jup_idx - moon_idx) % 12) + 1
            last_sign = jup_sign

            if house in jup_good:
                events.append(LifeEvent(
                    start=dt,
                    end=dt + timedelta(days=int(365)),
                    category="career",
                    title=f"Jupiter in {jup_sign} (House {house} from Moon)",
                    description=f"Favourable Jupiter transit — house {house} from natal Moon. Growth in career and fortune.",
                    intensity="high",
                    score=1.5,
                    source="jupiter_transit",
                ))
            elif house in jup_bad:
                events.append(LifeEvent(
                    start=dt,
                    end=dt + timedelta(days=int(365)),
                    category="general",
                    title=f"Jupiter in {jup_sign} (House {house} from Moon)",
                    description=f"Challenging Jupiter transit — house {house} from natal Moon. Caution in expansion.",
                    intensity="moderate",
                    score=-0.8,
                    source="jupiter_transit",
                ))
        dt += step

    return events


def _saturn_transit_events(
    natal_moon_sign: str,
    range_start: datetime,
    range_end: datetime,
) -> list[LifeEvent]:
    from app.astrology.gochara import GOOD_HOUSES_FROM_NATAL_MOON, BAD_HOUSES_FROM_NATAL_MOON
    from app.core.enums import ZODIAC_SIGNS
    import swisseph as swe

    events: list[LifeEvent] = []
    moon_idx = ZODIAC_SIGNS.index(natal_moon_sign)

    sat_good = GOOD_HOUSES_FROM_NATAL_MOON.get("Saturn", set())
    sat_bad = BAD_HOUSES_FROM_NATAL_MOON.get("Saturn", set())

    step = timedelta(days=90)
    dt = range_start
    last_sign = None

    while dt <= range_end:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        utc = dt.astimezone(timezone.utc)
        jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60.0)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        result, _ = swe.calc_ut(jd, swe.SATURN, flags)
        sat_sign = ZODIAC_SIGNS[int(result[0] / 30) % 12]

        if sat_sign != last_sign:
            sat_idx = ZODIAC_SIGNS.index(sat_sign)
            house = ((sat_idx - moon_idx) % 12) + 1
            last_sign = sat_sign

            if house in sat_good:
                events.append(LifeEvent(
                    start=dt,
                    end=dt + timedelta(days=int(2.5 * 365)),
                    category="career",
                    title=f"Saturn in {sat_sign} (House {house} from Moon)",
                    description=(
                        f"Favourable Saturn transit — house {house} from natal Moon. "
                        f"Discipline and hard work yield tangible results. "
                        f"Good for career stability, property, and long-term gains."
                    ),
                    intensity="high",
                    score=1.2,
                    source="saturn_transit",
                ))
            elif house in sat_bad:
                events.append(LifeEvent(
                    start=dt,
                    end=dt + timedelta(days=int(2.5 * 365)),
                    category="general",
                    title=f"Saturn in {sat_sign} (House {house} from Moon)",
                    description=(
                        f"Challenging Saturn transit — house {house} from natal Moon. "
                        f"Expect delays, increased responsibilities, and tests of patience. "
                        f"Focus on discipline and avoid risky ventures."
                    ),
                    intensity="moderate",
                    score=-1.0,
                    source="saturn_transit",
                ))
        dt += step

    return events


def generate_life_timeline(
    birth_dt: datetime,
    natal_nakshatra: str,
    natal_moon_longitude: float,
    natal_moon_sign: str,
    yogas: list[YogaResult],
    range_start: datetime,
    range_end: datetime,
) -> list[LifeEvent]:
    mahadashas = compute_mahadashas(birth_dt, natal_nakshatra, natal_moon_longitude)

    all_events: list[LifeEvent] = []
    all_events.extend(_dasha_events(mahadashas, range_start, range_end))
    all_events.extend(_sade_sati_events(natal_moon_sign, range_start, range_end))
    all_events.extend(_yoga_events(yogas, range_start, range_end))
    all_events.extend(_jupiter_transit_events(natal_moon_sign, range_start, range_end))
    all_events.extend(_saturn_transit_events(natal_moon_sign, range_start, range_end))

    all_events.sort(key=lambda e: (e.start, -e.score))
    return all_events


def timeline_summary(events: list[LifeEvent]) -> dict[str, list[dict]]:
    by_category: dict[str, list[dict]] = {}
    for e in events:
        by_category.setdefault(e.category, []).append(e.to_dict())
    return by_category
