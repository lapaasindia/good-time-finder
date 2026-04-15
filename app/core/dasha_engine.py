"""
Dasha Engine — computes dasha timeline and active periods for a person.
"""

from __future__ import annotations

from datetime import datetime

from app.astrology.dasha import (
    DashaPeriod,
    compute_mahadashas,
    compute_antardashas,
    compute_pratyantardashas,
    dasha_bonus_for_category,
    get_active_dasha,
    get_active_dasha_full,
)
from app.astrology.calculations import moon_constellation, natal_moon_sign
from app.core.models import Person


def _natal_moon_longitude(person: Person) -> float:
    import swisseph as swe
    from app.astrology.calculations import _to_julian_day
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = _to_julian_day(person.birth_datetime)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    result, _ = swe.calc_ut(jd, swe.MOON, flags)
    return result[0]


class DashaEngine:
    def __init__(self, person: Person, lagna: str | None = None, planet_strengths: dict[str, float] | None = None, natal_houses: dict[str, int] | None = None) -> None:
        self.person = person
        self.lagna = lagna
        self.planet_strengths = planet_strengths or {}
        self.natal_houses = natal_houses or {}
        nakshatra = moon_constellation(person.birth_datetime, person.birth_location)
        moon_lon = _natal_moon_longitude(person)
        self._mahadashas = compute_mahadashas(person.birth_datetime, nakshatra, moon_lon)

    @property
    def mahadashas(self) -> list[DashaPeriod]:
        return self._mahadashas

    def active_at(self, dt: datetime) -> tuple[DashaPeriod | None, DashaPeriod | None]:
        return get_active_dasha(self._mahadashas, dt)

    def active_full_at(
        self, dt: datetime
    ) -> tuple[DashaPeriod | None, DashaPeriod | None, DashaPeriod | None]:
        return get_active_dasha_full(self._mahadashas, dt)

    def dasha_bonus(self, dt: datetime, category: str, transiting_planets: set[str] | None = None) -> float:
        maha, antar, prat = self.active_full_at(dt)
        return dasha_bonus_for_category(
            maha, antar, prat, category, 
            lagna=self.lagna,
            planet_strengths=self.planet_strengths,
            transiting_planets=transiting_planets,
            natal_houses=self.natal_houses,
        )

    def dasha_detail(self, dt: datetime) -> dict:
        maha, antar, prat = self.active_full_at(dt)
        def _period_dict(p: DashaPeriod | None) -> dict | None:
            if p is None:
                return None
            return {
                "planet": p.planet,
                "level": p.level,
                "start": p.start.isoformat(),
                "end": p.end.isoformat(),
                "duration_days": round(p.duration_days, 1),
            }
        return {
            "mahadasha": _period_dict(maha),
            "antardasha": _period_dict(antar),
            "pratyantardasha": _period_dict(prat),
            "dasha_string": (
                f"{maha.planet if maha else '?'}"
                f"-{antar.planet if antar else '?'}"
                f"-{prat.planet if prat else '?'}"
            ),
        }

    def dasha_sandhi_penalty(self, dt: datetime) -> float:
        """Dasha Sandhi — penalty for being near a dasha junction.

        The transition between two dasha periods (especially Maha and Antar)
        is considered highly inauspicious. Results during sandhi are mixed,
        unreliable, and often negative.

        Sandhi zone:
        - Last 10% of outgoing dasha AND first 10% of incoming dasha
        - Mahadasha sandhi: strongest penalty (-0.4)
        - Antardasha sandhi: moderate penalty (-0.25)
        - Pratyantardasha sandhi: mild penalty (-0.1)

        Returns 0.0 (no sandhi) to -0.75 (deep sandhi at multiple levels).
        """
        from datetime import timedelta

        penalty = 0.0
        maha, antar, prat = self.active_full_at(dt)

        def _sandhi_check(period: DashaPeriod | None, max_penalty: float) -> float:
            if period is None:
                return 0.0
            total_days = period.duration_days
            if total_days <= 0:
                return 0.0
            # Sandhi zone = 10% at each end
            sandhi_days = total_days * 0.10
            sandhi_td = timedelta(days=sandhi_days)

            days_from_start = (dt - period.start).total_seconds() / 86400
            days_to_end = (period.end - dt).total_seconds() / 86400

            if days_from_start < sandhi_days:
                # In start-sandhi (incoming period)
                ratio = 1.0 - (days_from_start / sandhi_days)
                return -max_penalty * ratio
            elif days_to_end < sandhi_days:
                # In end-sandhi (outgoing period)
                ratio = 1.0 - (days_to_end / sandhi_days)
                return -max_penalty * ratio
            return 0.0

        penalty += _sandhi_check(maha, 0.4)
        penalty += _sandhi_check(antar, 0.25)
        penalty += _sandhi_check(prat, 0.1)

        return round(penalty, 3)

    def dasha_timeline(
        self,
        start: datetime,
        end: datetime,
    ) -> list[DashaPeriod]:
        result = []
        for m in self._mahadashas:
            if m.end < start or m.start > end:
                continue
            result.append(m)
        return result
