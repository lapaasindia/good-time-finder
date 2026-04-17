# Good Time Finder

A Vedic astrology **muhurtha rule engine** in Python. Finds auspicious time windows for activities like Travel, Marriage, and Medical procedures by evaluating a configurable set of astrological rules across a time range.

Inspired by [VedAstro](https://vedastro.org/GoodTimeFinder.html).

## Setup

```bash
pip install -e ".[dev]"
```

> `pyswisseph` requires the Swiss Ephemeris files. They are bundled with the package.

## Run the API

```bash
uvicorn app.api.main:app --reload
```

API docs: http://localhost:8000/docs

## Example request

```bash
curl -X POST http://localhost:8000/find \
  -H "Content-Type: application/json" \
  -d '{
    "person": {
      "name": "Rahul",
      "birth_datetime": "1992-08-14T10:20:00+05:30",
      "birth_location": {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata"
      }
    },
    "query_location": {
      "latitude": 28.6139,
      "longitude": 77.2090,
      "timezone": "Asia/Kolkata"
    },
    "time_range": {
      "start": "2026-04-12T00:00:00+05:30",
      "end": "2026-04-14T00:00:00+05:30",
      "step_minutes": 15
    },
    "tags": ["travel"]
  }'
```

## Example response

```json
{
  "chart_signature": { ... },
  "predictions": {
    "travel": {
      "tag": "travel",
      "overall_period_score": 1.25,
      "domain_static_scores": {
        "career": 2.1,
        "travel": -0.5
      },
      "domain_confidences": {
        "career": 0.85,
        "travel": 0.6
      },
      "windows": [
        {
          "start_time": "2026-04-12T00:00:00+05:30",
          "end_time": "2026-04-12T00:15:00+05:30",
          "composite_score": 1.2,
          "confidence": 0.75,
          "panchang_score": 0.4,
          "kp_score": 2.0,
          ...
        }
      ]
    }
  }
}
```

## Run tests

```bash
pytest -v
```

## Architecture

```
app/
├── api/          → FastAPI routes
├── astrology/    → Swiss Ephemeris calculations
├── core/         → engine, scoring, window-merge
├── rules/        → muhurtha rule classes + registry
├── config/       → events.yaml event catalog
└── services/     → high-level orchestrator
```

## Adding a new rule

1. Add entry in `app/config/events.yaml` with a unique `rule_key`.
2. Create a class in the relevant `app/rules/<category>.py` that extends `MuhurthaRule`.
3. Register it in `app/rules/registry.py`.
