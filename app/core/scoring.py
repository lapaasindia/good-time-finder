import math

from app.core.enums import EventNature

NATURE_SCORE: dict[EventNature, float] = {
    EventNature.GOOD: 3.0,
    EventNature.BAD: -3.0,
    EventNature.NEUTRAL: 0.0,
}


def score_event(nature: EventNature, weight: float = 1.0) -> float:
    return NATURE_SCORE.get(nature, 0.0) * weight


def rank_window(avg_score: float, duration_minutes: float) -> float:
    """Rank formula: score * log(1 + duration). Favors strong + long windows."""
    if duration_minutes <= 0:
        return 0.0
    return avg_score * math.log1p(duration_minutes)


from app.core.ranking import compute_composite_score, rank_window as composite_rank_window  # noqa: E402, F401
