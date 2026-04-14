"""
Sade Sati — Saturn's 7.5-year transit.

Sade Sati occurs when transiting Saturn passes through:
  - The sign 12th from natal Moon  (rising phase)
  - The natal Moon sign itself      (peak phase)
  - The sign 2nd from natal Moon   (setting phase)

Each phase lasts ~2.5 years (Saturn stays ~2.5 yrs per sign).

This is one of the most significant timing indicators in Vedic astrology,
associated with challenges, hard work, restructuring, and karmic lessons.

Also computes Shani Dhaiya (Small Panoti) — Saturn transiting the 4th or
8th sign from natal Moon for ~2.5 years each.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import swisseph as swe

from app.core.enums import ZODIAC_SIGNS


@dataclass
class SadeSatiPhase:
    phase: str
    saturn_sign: str
    start: datetime
    end: datetime
    intensity: str

    @property
    def duration_days(self) -> float:
        return (self.end - self.start).total_seconds() / 86400


@dataclass
class SadeSatiResult:
    natal_moon_sign: str
    phases: list[SadeSatiPhase]
    currently_active: bool
    current_phase: SadeSatiPhase | None
    dhaiya_active: bool
    dhaiya_sign: str | None
    penalty: float

    def summary(self) -> str:
        if self.currently_active and self.current_phase:
            return (
                f"Sade Sati ACTIVE — {self.current_phase.phase} phase "
                f"(Saturn in {self.current_phase.saturn_sign}). "
                f"Intensity: {self.current_phase.intensity}."
            )
        if self.dhaiya_active:
            return f"Shani Dhaiya ACTIVE — Saturn in {self.dhaiya_sign}."
        return "No Sade Sati or Dhaiya active."


SATURN_YEAR_PER_SIGN = 2.47


def _sign_index(sign: str) -> int:
    return ZODIAC_SIGNS.index(sign)


def _sign_at_offset(base_sign: str, offset: int) -> str:
    idx = (_sign_index(base_sign) + offset) % 12
    return ZODIAC_SIGNS[idx]


def _saturn_sign_at(dt: datetime) -> str:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    utc = dt.astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute / 60.0 + utc.second / 3600.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    result, _ = swe.calc_ut(jd, swe.SATURN, flags)
    lon = result[0]
    return ZODIAC_SIGNS[int(lon / 30) % 12]


def _find_saturn_sign_entry(sign: str, search_from: datetime, direction: int = 1) -> datetime:
    """Binary-search for when Saturn enters (direction=1) or exits (direction=-1) a sign."""
    step = timedelta(days=30 * direction)
    dt = search_from
    for _ in range(400):
        current_sign = _saturn_sign_at(dt)
        if direction == 1 and current_sign == sign:
            break
        if direction == -1 and current_sign != sign:
            break
        dt += step

    low = dt - step
    high = dt
    if low > high:
        low, high = high, low

    for _ in range(30):
        mid = low + (high - low) / 2
        mid_sign = _saturn_sign_at(mid)
        if mid_sign == sign:
            high = mid
        else:
            low = mid
    return high


def _saturn_transit_window(sign: str, near_dt: datetime) -> tuple[datetime, datetime]:
    """Find entry and exit dates for Saturn in a given sign near near_dt."""
    entry = _find_saturn_sign_entry(sign, near_dt - timedelta(days=900), direction=1)
    exit_ = entry + timedelta(days=int(SATURN_YEAR_PER_SIGN * 365.25))
    refined_exit = _find_saturn_sign_entry(
        ZODIAC_SIGNS[(_sign_index(sign) + 1) % 12],
        exit_ - timedelta(days=180),
        direction=1,
    )
    return entry, refined_exit


def compute_sade_sati(
    natal_moon_sign: str,
    reference_dt: datetime,
) -> SadeSatiResult:
    sign_12 = _sign_at_offset(natal_moon_sign, -1)
    sign_moon = natal_moon_sign
    sign_2 = _sign_at_offset(natal_moon_sign, 1)
    sign_4 = _sign_at_offset(natal_moon_sign, 3)
    sign_8 = _sign_at_offset(natal_moon_sign, 7)

    phases: list[SadeSatiPhase] = []
    for saturn_sign, phase_name, intensity in [
        (sign_12,  "Rising",  "moderate"),
        (sign_moon, "Peak",   "high"),
        (sign_2,   "Setting", "moderate"),
    ]:
        try:
            entry, exit_ = _saturn_transit_window(saturn_sign, reference_dt)
            phases.append(SadeSatiPhase(
                phase=phase_name,
                saturn_sign=saturn_sign,
                start=entry,
                end=exit_,
                intensity=intensity,
            ))
        except Exception:
            pass

    current_saturn_sign = _saturn_sign_at(reference_dt)
    currently_active = current_saturn_sign in {sign_12, sign_moon, sign_2}
    current_phase = None
    if currently_active:
        for p in phases:
            if p.saturn_sign == current_saturn_sign:
                current_phase = p
                break

    dhaiya_active = current_saturn_sign in {sign_4, sign_8}
    dhaiya_sign = current_saturn_sign if dhaiya_active else None

    penalty = 0.0
    if currently_active:
        penalty = -2.0 if current_phase and current_phase.phase == "Peak" else -1.0
    elif dhaiya_active:
        penalty = -0.5

    return SadeSatiResult(
        natal_moon_sign=natal_moon_sign,
        phases=phases,
        currently_active=currently_active,
        current_phase=current_phase,
        dhaiya_active=dhaiya_active,
        dhaiya_sign=dhaiya_sign,
        penalty=penalty,
    )
