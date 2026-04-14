"""Integration tests for the FastAPI endpoints using TestClient."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


_VALID_PAYLOAD = {
    "person": {
        "name": "Rahul",
        "birth_datetime": "1992-08-14T10:20:00+05:30",
        "birth_location": {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata",
        },
    },
    "query_location": {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata",
    },
    "time_range": {
        "start": "2026-04-12T00:00:00+05:30",
        "end": "2026-04-12T03:00:00+05:30",
        "step_minutes": 15,
    },
    "tags": ["travel"],
}


def test_invalid_time_range_returns_400():
    payload = dict(_VALID_PAYLOAD)
    payload["time_range"] = {
        "start": "2026-04-12T06:00:00+05:30",
        "end": "2026-04-12T00:00:00+05:30",
        "step_minutes": 15,
    }
    response = client.post("/find", json=payload)
    assert response.status_code == 400


def test_find_returns_expected_schema():
    """Smoke test with a mocked service to avoid real ephemeris calls."""
    from app.services.finder import FinderResult

    with patch("app.api.main._service") as mock_svc:
        mock_svc.find.return_value = FinderResult(windows=[], combined_windows=[])
        response = client.post("/find", json=_VALID_PAYLOAD)

    assert response.status_code == 200
    data = response.json()
    assert "windows" in data
    assert "combined_windows" in data
    assert "total_windows" in data
    assert "top_combined_windows" in data
