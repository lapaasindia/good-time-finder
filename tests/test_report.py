import pytest
from datetime import datetime, timezone
from app.core.models import Person, GeoLocation
from app.services.report_generator import generate_full_report_data
from app.services.pdf_builder import build_pdf_report

def test_generate_full_report_data():
    person = Person(
        name="Test User",
        birth_datetime=datetime(1990, 1, 1, 12, 0, tzinfo=timezone.utc),
        birth_location=GeoLocation(latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata")
    )
    report = generate_full_report_data(person)
    
    assert "personal_info" in report
    assert "reader_guide" in report
    assert "executive_summary" in report
    assert "chart_basics" in report
    assert "timing_overview" in report
    assert "planetary_positions" in report
    assert "houses_info" in report
    assert "yogas" in report
    assert "remedies" in report
    assert "action_plan" in report
    assert "lal_kitab" in report["remedies"]
    assert "current_dasha" in report
    assert report["executive_summary"]["headline"]
    assert report["executive_summary"]["strengths"]
    assert report["reader_guide"]["overview"]
    assert len(report["reader_guide"]["terms"]) >= 5
    assert report["chart_basics"]["plain_english"]
    assert report["timing_overview"]["timing_band"]
    assert report["timing_overview"]["plain_english"]
    assert report["action_plan"]["lean_into"]

    assert len(report["planetary_positions"]) >= 7
    assert len(report["houses_info"]) == 12
    assert report["planetary_positions"][0]["interpretation_en"]
    assert report["planetary_positions"][0]["strength_band"]
    assert report["houses_info"][0]["interpretation_en"]
    assert report["synthesis"][0]["score_band"]
    assert report["synthesis"][0]["confidence"]
    assert report["synthesis"][0]["plain_english"]
    assert report["synthesis"][0]["focus_now"]

def test_build_pdf_report():
    person = Person(
        name="PDF Test User",
        birth_datetime=datetime(1990, 1, 1, 12, 0, tzinfo=timezone.utc),
        birth_location=GeoLocation(latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata")
    )
    report = generate_full_report_data(person)
    pdf_bytes = build_pdf_report(report)
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000  # Should be a reasonably sized PDF
    assert pdf_bytes.startswith(b"%PDF-")
