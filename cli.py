#!/usr/bin/env python3
"""
Life Predictor — Command Line Interface

Usage examples:
  python cli.py natal   --name "Sahil" --birth "1992-08-14T04:50:00+00:00" --lat 28.6139 --lon 77.209
  python cli.py predict --name "Sahil" --birth "1992-08-14T04:50:00+00:00" --lat 28.6139 --lon 77.209 --category career --start 2025-06-01 --end 2025-07-01
  python cli.py doshas  --name "Sahil" --birth "1992-08-14T04:50:00+00:00" --lat 28.6139 --lon 77.209
  python cli.py sade_sati --name "Sahil" --birth "1992-08-14T04:50:00+00:00" --lat 28.6139 --lon 77.209 --date 2025-06-01
  python cli.py timeline --name "Sahil" --birth "1992-08-14T04:50:00+00:00" --lat 28.6139 --lon 77.209 --start 2025-01-01 --end 2030-01-01
  python cli.py panchang --birth "2025-06-01T10:00:00+00:00" --lat 28.6139 --lon 77.209
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

_BASE = None


def _make_person(name: str, birth_str: str, lat: float, lon: float, tz: str = "UTC"):
    from app.core.models import GeoLocation, Person
    birth_dt = datetime.fromisoformat(birth_str)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    return Person(
        name=name,
        birth_datetime=birth_dt,
        birth_location=GeoLocation(latitude=lat, longitude=lon, timezone=tz),
    )


def _make_location(lat: float, lon: float, tz: str = "UTC"):
    from app.core.models import GeoLocation
    return GeoLocation(latitude=lat, longitude=lon, timezone=tz)


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _sep():
    print("─" * 60)


def _print_kv(key: str, value, indent: int = 0):
    prefix = "  " * indent
    print(f"{prefix}{key:30s}  {value}")


# ─── natal ────────────────────────────────────────────────────

def cmd_natal(args):
    from app.astrology.calculations import (
        natal_lagna, natal_moon_sign, planet_houses, planet_signs,
    )
    from app.astrology.shadbala import shadbala_summary
    from app.core.yoga_engine import YogaEngine

    person = _make_person(args.name, args.birth, args.lat, args.lon, args.tz)

    print(f"\n{'═'*60}")
    print(f"  NATAL CHART  — {person.name}")
    print(f"  Birth: {person.birth_datetime.isoformat()}")
    _sep()

    lagna = natal_lagna(person)
    moon_s = natal_moon_sign(person)
    p_signs = planet_signs(person.birth_datetime, person.birth_location)
    p_houses = planet_houses(person.birth_datetime, person.birth_location)
    shadbala = shadbala_summary(p_signs, p_houses)

    _print_kv("Lagna (Ascendant)", lagna)
    _print_kv("Natal Moon Sign", moon_s)
    _sep()
    print("  Planetary Positions:")
    for planet, sign in p_signs.items():
        house = p_houses.get(planet, "?")
        strength = shadbala.get(planet, 0)
        strength_label = "strong" if strength >= 1.2 else ("weak" if strength < 0.7 else "medium")
        print(f"    {planet:10s}  {sign:15s}  House {house:2}  Shadbala: {strength:.2f} ({strength_label})")

    _sep()
    print("  Natal Yogas:")
    engine = YogaEngine(person)
    active = [y for y in engine.yogas if y.present]
    if active:
        for y in active:
            print(f"    ✓ {y.name:30s}  strength={y.strength:.2f}  [{y.category}]")
            print(f"      {y.description}")
    else:
        print("    No major yogas detected.")
    print()


# ─── predict ──────────────────────────────────────────────────

def cmd_predict(args):
    from app.core.models import TimeRange
    from app.services.life_predictor import LifePredictorService

    person = _make_person(args.name, args.birth, args.lat, args.lon, args.tz)
    location = _make_location(args.lat, args.lon, args.tz)
    start = _parse_dt(args.start)
    end = _parse_dt(args.end)
    time_range = TimeRange(start=start, end=end, step_minutes=args.step)

    print(f"\n{'═'*60}")
    print(f"  LIFE PREDICTION  — {person.name}  |  Category: {args.category.upper()}")
    print(f"  Period: {start.date()} → {end.date()}")
    _sep()

    svc = LifePredictorService()
    result = svc.predict(person, location, time_range, args.category)

    _print_kv("Natal Lagna", result.natal_lagna)
    _print_kv("Natal Moon Sign", result.natal_moon_sign)
    _print_kv("Overall Period Score", result.overall_period_score)
    _print_kv("Panchang Score", result.panchang_score)
    _print_kv("Gochara Score", result.gochara_score)
    _sep()
    print("  Active Dashas:")
    for d in result.active_dashas:
        print(f"    {d['level']:15s}  {d['planet']:10s}  {d['start'][:10]} → {d['end'][:10]}")
    _sep()
    print("  Sade Sati:")
    ss = result.sade_sati
    print(f"    {ss['summary']}")
    _sep()
    print("  Special Conditions:")
    sc = result.special_conditions
    print(f"    Kaal Sarp Dosha : {sc.get('kaal_sarp_dosha', False)} {sc.get('kaal_sarp_type','')}")
    print(f"    Mangal Dosha    : {sc.get('mangal_dosha', False)}")
    combust = sc.get('combust_planets', [])
    print(f"    Combust Planets : {', '.join(combust) if combust else 'None'}")
    retro = sc.get('retrograde_planets', [])
    print(f"    Retrograde      : {', '.join(retro) if retro else 'None'}")
    _sep()
    print("  Narrative:")
    print(f"    {result.narrative}")
    _sep()
    print(f"  Top Auspicious Windows (out of {len(result.windows)} total):")
    good = [w for w in result.windows if w.composite_score > 0]
    good.sort(key=lambda x: -x.rank)
    for i, w in enumerate(good[:8], 1):
        print(f"    {i}. {w.start.strftime('%Y-%m-%d %H:%M')} → {w.end.strftime('%Y-%m-%d %H:%M')}"
              f"  score={w.composite_score:.2f}  rank={w.rank:.2f}  ({w.nature})")
    print()


# ─── doshas ───────────────────────────────────────────────────

def cmd_doshas(args):
    from app.astrology.calculations import natal_lagna, planet_houses, planet_signs
    from app.astrology.special_conditions import compute_special_conditions

    person = _make_person(args.name, args.birth, args.lat, args.lon, args.tz)

    print(f"\n{'═'*60}")
    print(f"  DOSHAS & SPECIAL CONDITIONS  — {person.name}")
    _sep()

    lagna = natal_lagna(person)
    p_houses = planet_houses(person.birth_datetime, person.birth_location)
    p_signs = planet_signs(person.birth_datetime, person.birth_location)
    sc = compute_special_conditions(person.birth_datetime, p_houses, p_signs, lagna)

    _print_kv("Kaal Sarp Dosha", f"{'YES ⚠' if sc.kaal_sarp_dosha else 'No'}  {sc.kaal_sarp_type}")
    _print_kv("Mangal Dosha", "YES ⚠" if sc.mangal_dosha else "No")
    if sc.mangal_dosha:
        for pos in sc.mangal_dosha_positions:
            print(f"    → {pos}")
    _sep()
    print("  Combustion:")
    for planet, res in sc.combustion.items():
        status = f"COMBUST (orb {res.orb_degrees}°)" if res.combust else f"clear (orb {res.orb_degrees}°)"
        print(f"    {planet:10s}  {status}")
    _sep()
    print("  Retrograde:")
    for planet, res in sc.retrograde.items():
        print(f"    {planet:10s}  {'RETROGRADE ℞' if res.retrograde else 'Direct'}")
    _sep()
    graha = sc.graha_yuddha
    print(f"  Graha Yuddha (Planetary War): {'None' if not graha else ''}")
    for g in graha:
        print(f"    {g.winner} wins over {g.loser} (orb {g.orb}°)")
    _print_kv("Overall Penalty Score", sc.overall_penalty)
    print()


# ─── sade_sati ────────────────────────────────────────────────

def cmd_sade_sati(args):
    from app.astrology.calculations import natal_moon_sign
    from app.astrology.sade_sati import compute_sade_sati

    person = _make_person(args.name, args.birth, args.lat, args.lon, args.tz)
    ref_date = _parse_dt(args.date) if args.date else datetime.now(tz=timezone.utc)

    print(f"\n{'═'*60}")
    print(f"  SADE SATI / DHAIYA  — {person.name}")
    print(f"  Reference date: {ref_date.date()}")
    _sep()

    n_moon = natal_moon_sign(person)
    result = compute_sade_sati(n_moon, ref_date)

    _print_kv("Natal Moon Sign", result.natal_moon_sign)
    print()
    print(f"  Status: {result.summary()}")
    print()
    print("  All Sade Sati Phases (near reference date):")
    for p in result.phases:
        marker = "◄ ACTIVE" if (p.start <= ref_date < p.end) else ""
        print(f"    {p.phase:10s}  Saturn in {p.saturn_sign:15s}  "
              f"{p.start.strftime('%Y-%m-%d')} → {p.end.strftime('%Y-%m-%d')}  "
              f"intensity={p.intensity}  {marker}")
    print()


# ─── timeline ─────────────────────────────────────────────────

def cmd_timeline(args):
    from app.astrology.calculations import (
        natal_moon_sign, natal_lagna, planet_houses, planet_signs, moon_constellation,
    )
    from app.astrology.yogas import detect_all_yogas
    from app.astrology.extra_yogas import detect_all_extra_yogas
    from app.core.life_timeline import generate_life_timeline, timeline_summary
    import swisseph as swe
    from datetime import timezone as _tz

    person = _make_person(args.name, args.birth, args.lat, args.lon, args.tz)
    start = _parse_dt(args.start)
    end = _parse_dt(args.end)

    print(f"\n{'═'*60}")
    print(f"  LIFE TIMELINE  — {person.name}")
    print(f"  Period: {start.date()} → {end.date()}")
    _sep()

    n_moon = natal_moon_sign(person)
    lagna = natal_lagna(person)
    p_houses = planet_houses(person.birth_datetime, person.birth_location)
    p_signs = planet_signs(person.birth_datetime, person.birth_location)

    utc_birth = person.birth_datetime.astimezone(_tz.utc)
    jd = swe.julday(utc_birth.year, utc_birth.month, utc_birth.day,
                    utc_birth.hour + utc_birth.minute / 60.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon_result, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    natal_moon_lon = moon_result[0]
    natal_nak = moon_constellation(person.birth_datetime, person.birth_location)

    yogas = detect_all_yogas(p_houses, p_signs, lagna) + detect_all_extra_yogas(p_houses, p_signs, lagna)

    events = generate_life_timeline(
        birth_dt=person.birth_datetime,
        natal_nakshatra=natal_nak,
        natal_moon_longitude=natal_moon_lon,
        natal_moon_sign=n_moon,
        yogas=yogas,
        range_start=start,
        range_end=end,
    )

    by_cat = timeline_summary(events)
    for cat, cat_events in sorted(by_cat.items()):
        print(f"\n  [{cat.upper()}]")
        for e in cat_events:
            score_str = f"+{e['score']:.1f}" if e['score'] >= 0 else f"{e['score']:.1f}"
            print(f"    {e['start'][:10]} → {e['end'][:10]}  {score_str:6s}  {e['title']}")
            print(f"      {e['description'][:80]}")
    print()


# ─── panchang ─────────────────────────────────────────────────

def cmd_panchang(args):
    from app.astrology.calculations import (
        lunar_day, moon_constellation, weekday,
    )
    from app.astrology.panchang import build_panchang

    birth_dt = _parse_dt(args.birth)
    loc = _make_location(args.lat, args.lon, args.tz)

    print(f"\n{'═'*60}")
    print(f"  PANCHANG  — {birth_dt.strftime('%Y-%m-%d %H:%M %Z')}")
    _sep()

    tithi = lunar_day(birth_dt, loc)
    nak = moon_constellation(birth_dt, loc)
    wd = weekday(birth_dt)
    p = build_panchang(birth_dt, nak, tithi, wd)

    _print_kv("Tithi (Lunar Day)", tithi)
    _print_kv("Nakshatra", nak)
    _print_kv("Vara (Weekday)", wd)
    _print_kv("Yoga", f"{p.yoga_name}  ({p.yoga_nature})")
    _print_kv("Karana", f"{p.karana_name}  ({p.karana_nature})")
    _print_kv("Auspicious?", "✓ Yes" if p.is_auspicious() else "✗ No")
    _print_kv("Yoga Score", p.yoga_score)
    _print_kv("Karana Score", p.karana_score)
    print()


# ─── main ─────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="life-predictor",
        description="Vedic Astrology Life Predictor — CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--name",  required=True,  help="Person's name")
    shared.add_argument("--birth", required=True,  help="Birth datetime ISO 8601 e.g. 1992-08-14T04:50:00+00:00")
    shared.add_argument("--lat",   type=float, required=True,  help="Birth latitude")
    shared.add_argument("--lon",   type=float, required=True,  help="Birth longitude")
    shared.add_argument("--tz",    default="UTC", help="Timezone name e.g. Asia/Kolkata (default: UTC)")

    # natal
    sub.add_parser("natal", parents=[shared], help="Show natal chart, shadbala, and yogas")

    # predict
    pred = sub.add_parser("predict", parents=[shared], help="Predict best windows for a category")
    pred.add_argument("--category", default="general",
                      choices=["career","finance","health","marriage","education",
                               "property","children","spirituality","legal","travel","general"])
    pred.add_argument("--start",  required=True, help="Range start date e.g. 2025-06-01")
    pred.add_argument("--end",    required=True, help="Range end date   e.g. 2025-07-01")
    pred.add_argument("--step",   type=int, default=60, help="Step in minutes (default 60)")

    # doshas
    sub.add_parser("doshas", parents=[shared], help="Show Kaal Sarp, Mangal Dosha, combustion, retrograde")

    # sade_sati
    ss = sub.add_parser("sade_sati", parents=[shared], help="Show Sade Sati and Dhaiya status")
    ss.add_argument("--date", default=None, help="Reference date (default: today)")

    # timeline
    tl = sub.add_parser("timeline", parents=[shared], help="Multi-year life event timeline")
    tl.add_argument("--start", required=True, help="Timeline start e.g. 2025-01-01")
    tl.add_argument("--end",   required=True, help="Timeline end   e.g. 2030-01-01")

    # panchang
    pan = sub.add_parser("panchang", help="Show Panchang for a given datetime and location")
    pan.add_argument("--birth", required=True, help="Datetime ISO 8601")
    pan.add_argument("--lat",   type=float, required=True)
    pan.add_argument("--lon",   type=float, required=True)
    pan.add_argument("--tz",    default="UTC")

    return parser


COMMANDS = {
    "natal":     cmd_natal,
    "predict":   cmd_predict,
    "doshas":    cmd_doshas,
    "sade_sati": cmd_sade_sati,
    "timeline":  cmd_timeline,
    "panchang":  cmd_panchang,
}


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        COMMANDS[args.command](args)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
