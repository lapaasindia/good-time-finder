from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.services.life_predictor import PredictionWindow, _build_narrative


def test_build_narrative_uses_plain_language_and_window_guidance():
    start = datetime(2026, 4, 12, 9, 0, tzinfo=timezone.utc)
    good_window = PredictionWindow(
        start=start,
        end=start + timedelta(hours=2),
        nature="good",
        composite_score=1.8,
        rank=5.0,
        duration_minutes=120,
    )
    hard_window = PredictionWindow(
        start=start + timedelta(hours=5),
        end=start + timedelta(hours=7),
        nature="bad",
        composite_score=-1.4,
        rank=-3.0,
        duration_minutes=120,
    )

    narrative = _build_narrative(
        category="career",
        maha=SimpleNamespace(planet="Jupiter"),
        antar=SimpleNamespace(planet="Rahu"),
        active_yogas=[{"name": "GajakesariYoga"}, {"name": "BudhaAdityaYoga"}],
        gochara_score=-0.2,
        shadbala={"Sun": 1.4, "Jupiter": 1.3, "Mars": 0.8},
        overall_score=0.9,
        sade_sati=SimpleNamespace(
            currently_active=True,
            current_phase=SimpleNamespace(phase="Setting", saturn_sign="Pisces"),
            dhaiya_active=False,
            dhaiya_sign=None,
        ),
        special=SimpleNamespace(
            kaal_sarp_dosha=False,
            kaal_sarp_type="",
            mangal_dosha=True,
            combustion={"Sun": SimpleNamespace(combust=False)},
            retrograde={"Saturn": SimpleNamespace(retrograde=True)},
        ),
        panchang=SimpleNamespace(
            yoga_nature="bad",
            yoga_name="Atiganda",
            karana_name="Vishti",
            karana_nature="bad",
        ),
        windows=[good_window, hard_window],
    )

    assert "career and professional decisions look supportive overall" in narrative.lower()
    assert "main timing cycle is Jupiter" in narrative
    assert "best window in this range" in narrative
    assert "touchier patch" in narrative
    assert "Helpful natal combinations in the background include" in narrative
    assert "Mahadasha is active" not in narrative
    assert "inauspicious" not in narrative
    assert "⚠" not in narrative
