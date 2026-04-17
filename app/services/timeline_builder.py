"""
Timeline Builder
Samples the next 12 months using the Heatmap engine (LifePredictorService)
to give a quick overview for the report.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.core.models import GeoLocation, Person, TimeRange
from app.services.life_predictor import LifePredictorService


def build_domain_timeline(
    person: Person,
    category: str,
    start_dt: datetime,
    months: int = 12,
    predictor: LifePredictorService | None = None
) -> list[dict]:
    """
    Run a high-level scan of the next `months` months.
    Returns a list of dicts: {"month": "Jan 2025", "score": 1.5, "band": "Strong"}
    """
    if predictor is None:
        predictor = LifePredictorService()
        
    timeline = []
    
    # Evaluate at a rough monthly interval (1 window per month)
    # This is a low-res scan to keep report generation fast.
    for i in range(months):
        dt_month = start_dt + timedelta(days=30 * i)
        
        # Look at a 3-day window in the middle of the month
        # Large step size to minimize computation (24h)
        tr = TimeRange(
            start=dt_month,
            end=dt_month + timedelta(days=3),
            step_minutes=1440
        )
        
        res = predictor.predict(
            person=person,
            location=person.birth_location, # Default to birth loc for long term transits
            time_range=tr,
            category=category
        )
        
        score = res.overall_period_score
        
        if score >= 2.2:
            band = "Exceptional"
        elif score >= 1.0:
            band = "Strong"
        elif score >= -0.5:
            band = "Moderate"
        elif score >= -1.5:
            band = "Strained"
        else:
            band = "Challenging"
            
        timeline.append({
            "month": dt_month.strftime("%b %Y"),
            "score": score,
            "band": band
        })
        
    return timeline
