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
    assert "planetary_positions" in report
    assert "houses_info" in report
    assert "yogas" in report
    assert "remedies" in report
    assert "lal_kitab" in report["remedies"]
    assert "current_dasha" in report
    
    assert len(report["planetary_positions"]) >= 7
    assert len(report["houses_info"]) == 12

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
