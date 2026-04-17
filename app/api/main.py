from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
import os

from app.core.enums import EventNature, EventTag
from app.core.models import GeoLocation, Person, TimeRange
from app.services.finder import CombinedWindow, FinderResult, GoodTimeFinderService
from app.services.life_predictor import LifePredictorService, LifePrediction, PredictionWindow
from app.services.report_generator import generate_full_report_data
from app.services.pdf_builder import build_pdf_report

app = FastAPI(
    title="Life Predictor",
    description="Vedic astrology life prediction engine — muhurtha, dasha, gochara, yogas, shadbala.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_UI_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "life_predictor_ui.html")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui")

@app.get("/ui", include_in_schema=False)
def serve_ui():
    path = os.path.abspath(_UI_FILE)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(
        content=content,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )

_service = GoodTimeFinderService()
_predictor = LifePredictorService()


# ──────────────────────────────────────────
# Request / Response schemas
# ──────────────────────────────────────────


class GeoLocationSchema(BaseModel):
    latitude: float
    longitude: float
    timezone: str


class PersonSchema(BaseModel):
    name: str
    birth_datetime: datetime
    birth_location: GeoLocationSchema


class TimeRangeSchema(BaseModel):
    start: datetime
    end: datetime
    step_minutes: Annotated[int, Field(default=15, ge=1, le=1440)]


class FindRequest(BaseModel):
    person: PersonSchema
    query_location: GeoLocationSchema
    time_range: TimeRangeSchema
    tags: list[EventTag] = Field(default=[EventTag.GENERAL])


class TimeWindowResponse(BaseModel):
    event_name: str
    start: datetime
    end: datetime
    nature: EventNature
    description: str
    score: float
    tags: list[EventTag]
    duration_minutes: float


class CombinedWindowResponse(BaseModel):
    start: datetime
    end: datetime
    total_score: float
    rank: float
    duration_minutes: float
    active_events: list[str]


class FindResponse(BaseModel):
    windows: list[TimeWindowResponse]
    combined_windows: list[CombinedWindowResponse]
    total_windows: int
    top_combined_windows: list[CombinedWindowResponse]


# ──────────────────────────────────────────
# Routes
# ──────────────────────────────────────────


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/find", response_model=FindResponse)
def find_good_times(req: FindRequest) -> FindResponse:
    if req.time_range.start >= req.time_range.end:
        raise HTTPException(
            status_code=400,
            detail="time_range.start must be before time_range.end",
        )

    person = Person(
        name=req.person.name,
        birth_datetime=req.person.birth_datetime,
        birth_location=GeoLocation(
            latitude=req.person.birth_location.latitude,
            longitude=req.person.birth_location.longitude,
            timezone=req.person.birth_location.timezone,
        ),
    )

    location = GeoLocation(
        latitude=req.query_location.latitude,
        longitude=req.query_location.longitude,
        timezone=req.query_location.timezone,
    )

    time_range = TimeRange(
        start=req.time_range.start,
        end=req.time_range.end,
        step_minutes=req.time_range.step_minutes,
    )

    result: FinderResult = _service.find(
        person=person,
        location=location,
        time_range=time_range,
        selected_tags=req.tags,
    )

    windows = [
        TimeWindowResponse(
            event_name=w.event_name,
            start=w.start,
            end=w.end,
            nature=w.nature,
            description=w.description,
            score=w.score,
            tags=w.tags,
            duration_minutes=w.duration_minutes,
        )
        for w in result.windows
    ]

    combined = [
        CombinedWindowResponse(
            start=c.start,
            end=c.end,
            total_score=c.total_score,
            rank=c.rank,
            duration_minutes=c.duration_minutes,
            active_events=c.active_events,
        )
        for c in result.combined_windows
    ]

    return FindResponse(
        windows=windows,
        combined_windows=combined,
        total_windows=len(windows),
        top_combined_windows=combined[:5],
    )


# ──────────────────────────────────────────
# Natal chart
# ──────────────────────────────────────────


class NatalRequest(BaseModel):
    person: PersonSchema
    location: GeoLocationSchema


@app.post("/natal")
def natal_chart(req: NatalRequest):
    from app.core.yoga_engine import YogaEngine
    from app.astrology.calculations import natal_lagna, natal_moon_sign, planet_houses, planet_signs, moon_constellation
    from app.astrology.shadbala import shadbala_summary
    from app.astrology.nakshatra_predictions import nakshatra_prediction_summary
    from app.astrology.divisional_charts import compute_d9_positions, compute_d10_positions
    from app.astrology.jaimini import compute_chara_karakas, compute_arudha_lagna
    from app.astrology.gulika_mandi import estimate_gulika_sign
    from app.astrology.special_conditions import get_raw_longitudes

    person = Person(
        name=req.person.name,
        birth_datetime=req.person.birth_datetime,
        birth_location=GeoLocation(
            latitude=req.person.birth_location.latitude,
            longitude=req.person.birth_location.longitude,
            timezone=req.person.birth_location.timezone,
        ),
    )

    yoga_engine = YogaEngine(person)
    p_signs = planet_signs(person.birth_datetime, person.birth_location)
    p_houses = planet_houses(person.birth_datetime, person.birth_location)
    shadbala = shadbala_summary(p_signs, p_houses)
    nakshatra = moon_constellation(person.birth_datetime, person.birth_location)
    nak_profile = nakshatra_prediction_summary(nakshatra)
    
    n_lagna = natal_lagna(person)
    raw_longitudes = get_raw_longitudes(person.birth_datetime)
    chara = compute_chara_karakas(raw_longitudes)
    arudha = compute_arudha_lagna(n_lagna, p_signs)
    
    weekday = person.birth_datetime.strftime("%A")
    birth_hour = person.birth_datetime.hour + person.birth_datetime.minute / 60.0
    gulika = estimate_gulika_sign(weekday, birth_hour, n_lagna)
    
    d9 = compute_d9_positions(raw_longitudes)
    d10 = compute_d10_positions(raw_longitudes)

    return {
        "natal_lagna": natal_lagna(person),
        "natal_moon_sign": natal_moon_sign(person),
        "natal_nakshatra": nakshatra,
        "nakshatra_profile": nak_profile,
        "planet_signs": p_signs,
        "planet_houses": p_houses,
        "shadbala": shadbala,
        "yoga_summary": yoga_engine.summary(),
        "advanced": {
            "chara_karakas": chara,
            "arudha_lagna": arudha,
            "gulika_sign": gulika,
            "d9_signs": d9,
            "d10_signs": d10
        }
    }


# ──────────────────────────────────────────
# Dasha timeline
# ──────────────────────────────────────────


class DashaRequest(BaseModel):
    person: PersonSchema
    start: datetime
    end: datetime


@app.post("/dashas")
def dasha_timeline(req: DashaRequest):
    from app.core.dasha_engine import DashaEngine

    person = Person(
        name=req.person.name,
        birth_datetime=req.person.birth_datetime,
        birth_location=GeoLocation(
            latitude=req.person.birth_location.latitude,
            longitude=req.person.birth_location.longitude,
            timezone=req.person.birth_location.timezone,
        ),
    )

    engine = DashaEngine(person)
    periods = engine.dasha_timeline(req.start, req.end)
    now_detail = engine.dasha_detail(req.start)

    return {
        "mahadashas": [
            {
                "planet": p.planet,
                "start": p.start.isoformat(),
                "end": p.end.isoformat(),
                "duration_days": round(p.duration_days, 1),
            }
            for p in periods
        ],
        "current_dasha": now_detail,
    }


# ──────────────────────────────────────────
# Gochara transit scores
# ──────────────────────────────────────────


class GocharaRequest(BaseModel):
    person: PersonSchema
    query_location: GeoLocationSchema
    date: datetime


@app.post("/gochara")
def gochara_scores(req: GocharaRequest):
    from app.astrology.calculations import build_context, natal_moon_sign, planet_signs, natal_lagna, planet_houses
    from app.astrology.gochara import gochara_score, total_gochara_score, _house_from_sign
    from app.astrology.ashtakavarga import ashtakavarga_bonus
    from app.astrology.shadbala import shadbala_summary

    person = Person(
        name=req.person.name,
        birth_datetime=req.person.birth_datetime,
        birth_location=GeoLocation(
            latitude=req.person.birth_location.latitude,
            longitude=req.person.birth_location.longitude,
            timezone=req.person.birth_location.timezone,
        ),
    )
    location = GeoLocation(
        latitude=req.query_location.latitude,
        longitude=req.query_location.longitude,
        timezone=req.query_location.timezone,
    )

    n_moon = natal_moon_sign(person)
    n_lagna = natal_lagna(person)
    natal_p_signs = planet_signs(person.birth_datetime, person.birth_location)
    natal_p_houses = planet_houses(person.birth_datetime, person.birth_location)
    from app.astrology.tara_bala import compute_tara, chandra_bala
    from app.astrology.avasthas import avastha_score_for_planets
    from app.astrology.special_conditions import get_speeds, get_raw_longitudes
    from app.astrology.sudarshana import sudarshana_aggregate
    from app.astrology.calculations import moon_constellation
    
    ctx = build_context(req.date, location, person)

    # Calculate advanced transit data
    natal_nak = moon_constellation(person.birth_datetime, person.birth_location)
    transit_nak = moon_constellation(req.date, location)
    tara_name, tara_score = compute_tara(natal_nak, transit_nak)
    
    transit_moon_house = _house_from_sign(ctx.planet_signs.get("Moon", ""), n_moon)
    chandra_score = chandra_bala(transit_moon_house)
    
    speeds = get_speeds(req.date)
    retrograde = [p for p, s in speeds.items() if s < 0]
    
    longitudes = get_raw_longitudes(req.date)
    avasthas = avastha_score_for_planets(longitudes, {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"})
    
    natal_sun = natal_p_signs.get("Sun", "")
    sudarshana = sudarshana_aggregate(ctx.planet_signs, n_lagna, n_moon, natal_sun)

    scores = gochara_score(ctx.planet_signs, n_moon)
    avarga = ashtakavarga_bonus(ctx.planet_signs, natal_p_signs, n_lagna)
    shadbala = shadbala_summary(natal_p_signs, natal_p_houses)

    return {
        "date": req.date.isoformat(),
        "natal_moon_sign": n_moon,
        "current_lagna": ctx.lagna,
        "current_planet_signs": ctx.planet_signs,
        "gochara_by_planet": scores,
        "total_gochara_score": total_gochara_score(ctx.planet_signs, n_moon),
        "ashtakavarga_bonus": avarga,
        "shadbala": shadbala,
        "advanced": {
            "tara_name": tara_name,
            "tara_score": tara_score,
            "chandra_bala": chandra_score,
            "retrograde_planets": retrograde,
            "avasthas": avasthas,
            "sudarshana_score": sudarshana
        }
    }


# ──────────────────────────────────────────
# Full life prediction
# ──────────────────────────────────────────

VALID_CATEGORIES = {
    "general", "travel", "marriage", "career", "finance",
    "health", "education", "property", "children", "spirituality", "legal",
    "fame", "business", "relationships", "accidents"
}


class PredictRequest(BaseModel):
    person: PersonSchema
    query_location: GeoLocationSchema
    time_range: TimeRangeSchema
    category: str = "general"


class PredictionWindowResponse(BaseModel):
    start: datetime
    end: datetime
    nature: str
    composite_score: float
    rank: float
    duration_minutes: float
    active_events: list[str]
    dasha_active: list[str]
    yogas_active: list[str]
    gochara_score: float
    shadbala_score: float
    dasha_bonus: float
    yoga_score: float
    rule_score: float
    tara_score: float
    chandra_bala_score: float
    avastha_score: float
    pushkara_bonus_score: float
    sudarshana_score: float
    sandhi_penalty: float
    bhrigu_bonus: float
    kp_score: float
    kp_cuspal_score: float
    double_transit: float


class PredictResponse(BaseModel):
    category: str
    person_name: str
    natal_lagna: str
    natal_moon_sign: str
    active_dashas: list[dict]
    yogas: list[dict]
    shadbala: dict[str, float]
    gochara_score: float
    sade_sati: dict
    special_conditions: dict
    panchang_score: float
    overall_period_score: float
    narrative: str
    top_windows: list[PredictionWindowResponse]
    all_windows: list[PredictionWindowResponse]
    total_windows: int
    jaimini_score: float
    arudha_score: float
    gulika_penalty: float
    badhaka_penalty: float
    divisional_scores: dict[str, float]
    bhrigu_bonus: float
    kp_score: float
    kp_cuspal_score: float
    double_transit: float


class LifePredictionRequest(BaseModel):
    name: str = Field(default="Native")
    birth_datetime: datetime
    latitude: float
    longitude: float
    timezone: str = Field(default="Asia/Kolkata")

@app.post(
    "/report",
    summary="Generate Comprehensive PDF Report",
    description="Returns a full astrology report covering personality, remedies, planets, houses, yogas, and dashas in PDF format.",
)
async def generate_pdf_report(request: LifePredictionRequest):
    try:
        person = Person(
            name=request.name,
            birth_datetime=request.birth_datetime,
            birth_location=GeoLocation(
                latitude=request.latitude,
                longitude=request.longitude,
                timezone=request.timezone
            )
        )
        report_data = generate_full_report_data(person)
        pdf_bytes = build_pdf_report(report_data)
        
        from io import BytesIO
        buffer = BytesIO(pdf_bytes)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.name}_Astrology_Report.pdf"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    if req.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{req.category}'. Must be one of: {sorted(VALID_CATEGORIES)}",
        )
    if req.time_range.start >= req.time_range.end:
        raise HTTPException(status_code=400, detail="time_range.start must be before end")

    person = Person(
        name=req.person.name,
        birth_datetime=req.person.birth_datetime,
        birth_location=GeoLocation(
            latitude=req.person.birth_location.latitude,
            longitude=req.person.birth_location.longitude,
            timezone=req.person.birth_location.timezone,
        ),
    )
    location = GeoLocation(
        latitude=req.query_location.latitude,
        longitude=req.query_location.longitude,
        timezone=req.query_location.timezone,
    )
    time_range = TimeRange(
        start=req.time_range.start,
        end=req.time_range.end,
        step_minutes=req.time_range.step_minutes,
    )

    result: LifePrediction = _predictor.predict(
        person=person,
        location=location,
        time_range=time_range,
        category=req.category,
    )

    return PredictResponse(
        category=result.category,
        person_name=result.person_name,
        natal_lagna=result.natal_lagna,
        natal_moon_sign=result.natal_moon_sign,
        active_dashas=result.active_dashas,
        yogas=result.yogas,
        shadbala=result.shadbala,
        gochara_score=result.gochara_score,
        sade_sati=result.sade_sati,
        special_conditions=result.special_conditions,
        panchang_score=result.panchang_score,
        overall_period_score=result.overall_period_score,
        narrative=result.narrative,
        top_windows=[
            PredictionWindowResponse(
                start=w.start,
                end=w.end,
                nature=w.nature,
                composite_score=w.composite_score,
                rank=w.rank,
                duration_minutes=w.duration_minutes,
                active_events=w.active_events,
                dasha_active=w.dasha_active,
                yogas_active=w.yogas_active,
                gochara_score=w.gochara_score,
                shadbala_score=w.shadbala_score,
                dasha_bonus=w.dasha_bonus,
                yoga_score=w.yoga_score,
                rule_score=w.rule_score,
                tara_score=w.tara_score,
                chandra_bala_score=w.chandra_bala_score,
                avastha_score=w.avastha_score,
                pushkara_bonus_score=w.pushkara_bonus_score,
                sudarshana_score=w.sudarshana_score,
                sandhi_penalty=w.sandhi_penalty,
                bhrigu_bonus=w.bhrigu_bonus,
                kp_score=w.kp_score,
                kp_cuspal_score=w.kp_cuspal_score,
                double_transit=w.double_transit,
            )
            for w in result.top_windows
        ],
        all_windows=[
            PredictionWindowResponse(
                start=w.start,
                end=w.end,
                nature=w.nature,
                composite_score=w.composite_score,
                rank=w.rank,
                duration_minutes=w.duration_minutes,
                active_events=w.active_events,
                dasha_active=w.dasha_active,
                yogas_active=w.yogas_active,
                gochara_score=w.gochara_score,
                shadbala_score=w.shadbala_score,
                dasha_bonus=w.dasha_bonus,
                yoga_score=w.yoga_score,
                rule_score=w.rule_score,
                tara_score=w.tara_score,
                chandra_bala_score=w.chandra_bala_score,
                avastha_score=w.avastha_score,
                pushkara_bonus_score=w.pushkara_bonus_score,
                sudarshana_score=w.sudarshana_score,
                sandhi_penalty=w.sandhi_penalty,
                bhrigu_bonus=w.bhrigu_bonus,
                kp_score=w.kp_score,
                kp_cuspal_score=w.kp_cuspal_score,
                double_transit=w.double_transit,
            )
            for w in result.windows
        ],
        total_windows=len(result.windows),
        jaimini_score=result.jaimini_score,
        arudha_score=result.arudha_score,
        gulika_penalty=result.gulika_penalty,
        badhaka_penalty=result.badhaka_penalty,
        divisional_scores=result.divisional_scores,
        bhrigu_bonus=result.bhrigu_bonus,
        kp_score=result.kp_score,
        kp_cuspal_score=result.kp_cuspal_score,
        double_transit=result.double_transit,
    )


# ──────────────────────────────────────────
# /sade_sati — Sade Sati and Dhaiya status
# ──────────────────────────────────────────

class SadeSatiRequest(BaseModel):
    person: PersonSchema
    reference_date: datetime


@app.post("/sade_sati")
def sade_sati_endpoint(req: SadeSatiRequest) -> dict:
    from app.astrology.calculations import natal_moon_sign as _natal_moon
    from app.astrology.sade_sati import compute_sade_sati
    from app.core.models import Person as _Person, GeoLocation as _GeoLocation

    person = _Person(
        name=req.person.name,
        birth_datetime=req.person.birth_datetime,
        birth_location=_GeoLocation(
            latitude=req.person.birth_location.latitude,
            longitude=req.person.birth_location.longitude,
            timezone=req.person.birth_location.timezone,
        ),
    )
    n_moon = _natal_moon(person)
    result = compute_sade_sati(n_moon, req.reference_date)
    return {
        "natal_moon_sign": result.natal_moon_sign,
        "currently_active": result.currently_active,
        "dhaiya_active": result.dhaiya_active,
        "dhaiya_sign": result.dhaiya_sign,
        "penalty": result.penalty,
        "summary": result.summary(),
        "phases": [
            {
                "phase": p.phase,
                "saturn_sign": p.saturn_sign,
                "start": p.start.isoformat(),
                "end": p.end.isoformat(),
                "intensity": p.intensity,
                "duration_days": round(p.duration_days, 1),
            }
            for p in result.phases
        ],
    }


# ──────────────────────────────────────────
# /doshas — Kaal Sarp, Mangal, combustion, retrograde
# ──────────────────────────────────────────

class DoshaRequest(BaseModel):
    person: PersonSchema


@app.post("/doshas")
def doshas_endpoint(req: DoshaRequest) -> dict:
    from app.astrology.calculations import (
        natal_lagna as _natal_lagna,
        planet_houses as _ph,
        planet_signs as _ps,
    )
    from app.astrology.special_conditions import compute_special_conditions
    from app.core.models import Person as _Person, GeoLocation as _GeoLocation

    person = _Person(
        name=req.person.name,
        birth_datetime=req.person.birth_datetime,
        birth_location=_GeoLocation(
            latitude=req.person.birth_location.latitude,
            longitude=req.person.birth_location.longitude,
            timezone=req.person.birth_location.timezone,
        ),
    )
    lagna = _natal_lagna(person)
    p_houses = _ph(person.birth_datetime, person.birth_location)
    p_signs = _ps(person.birth_datetime, person.birth_location)
    result = compute_special_conditions(person.birth_datetime, p_houses, p_signs, lagna)
    return result.summary()


# ──────────────────────────────────────────
# /timeline — Multi-year life event timeline
# ──────────────────────────────────────────

class TimelineRequest(BaseModel):
    person: PersonSchema
    start: datetime
    end: datetime


@app.post("/timeline")
def timeline_endpoint(req: TimelineRequest) -> dict:
    from app.astrology.calculations import (
        natal_moon_sign as _natal_moon,
        moon_sign as _moon_sign,
        planet_houses as _ph,
        planet_signs as _ps,
        natal_lagna as _natal_lagna,
    )
    from app.astrology.dasha import NAKSHATRA_LORD
    from app.astrology.calculations import moon_constellation as _nak
    from app.astrology.yogas import detect_all_yogas
    from app.astrology.extra_yogas import detect_all_extra_yogas
    from app.core.life_timeline import generate_life_timeline, timeline_summary
    from app.core.models import Person as _Person, GeoLocation as _GeoLocation
    import swisseph as swe

    person = _Person(
        name=req.person.name,
        birth_datetime=req.person.birth_datetime,
        birth_location=_GeoLocation(
            latitude=req.person.birth_location.latitude,
            longitude=req.person.birth_location.longitude,
            timezone=req.person.birth_location.timezone,
        ),
    )
    n_moon = _natal_moon(person)
    lagna = _natal_lagna(person)
    p_houses = _ph(person.birth_datetime, person.birth_location)
    p_signs = _ps(person.birth_datetime, person.birth_location)

    from datetime import timezone as _tz
    utc_birth = person.birth_datetime.astimezone(_tz.utc)
    jd = swe.julday(utc_birth.year, utc_birth.month, utc_birth.day,
                    utc_birth.hour + utc_birth.minute / 60.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    moon_result, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    natal_moon_lon = moon_result[0]
    natal_nak = _nak(person.birth_datetime, person.birth_location)

    yogas = detect_all_yogas(p_houses, p_signs, lagna) + detect_all_extra_yogas(p_houses, p_signs, lagna)

    events = generate_life_timeline(
        birth_dt=person.birth_datetime,
        natal_nakshatra=natal_nak,
        natal_moon_longitude=natal_moon_lon,
        natal_moon_sign=n_moon,
        yogas=yogas,
        range_start=req.start,
        range_end=req.end,
    )

    return {
        "total_events": len(events),
        "by_category": timeline_summary(events),
        "all_events": [e.to_dict() for e in events],
    }
