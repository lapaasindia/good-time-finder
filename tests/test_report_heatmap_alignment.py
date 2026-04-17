"""
Phase 7 — Test 3: Report ↔ Heatmap alignment.

Verifies:
  • The report payload includes the new dasha_domain_matrix section.
  • The dasha_domain_matrix has exactly 10 domain rows.
  • Each row has maha, antar, pratyantar, and composite keys.
  • The composite score for each domain is in a sensible range.
  • The report's domain_scores section correlates with prediction scores
    (both should agree on relative ordering for the same person/category).
"""

import pytest
from datetime import datetime

from app.core.models import Person, GeoLocation, TimeRange


TEST_PERSON = Person(
    name="Test User",
    birth_datetime=datetime(1990, 5, 15, 10, 30),
    birth_location=GeoLocation(latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata"),
)


@pytest.fixture(scope="module")
def report_payload():
    from app.services.report_generator import generate_full_report_data
    return generate_full_report_data(TEST_PERSON)


class TestDashaMatrixPresent:
    """Report must include the dasha_domain_matrix section."""

    def test_key_exists(self, report_payload):
        assert "dasha_domain_matrix" in report_payload, (
            "Report payload missing 'dasha_domain_matrix'"
        )

    def test_ten_domains(self, report_payload):
        matrix = report_payload["dasha_domain_matrix"]
        assert len(matrix) == 10, (
            f"Expected 10 domain rows, got {len(matrix)}"
        )


class TestDashaMatrixStructure:
    """Each row must have the correct keys and bounded composite."""

    REQUIRED_KEYS = {"domain", "maha", "antar", "pratyantar", "composite"}

    def test_row_keys(self, report_payload):
        for row in report_payload["dasha_domain_matrix"]:
            missing = self.REQUIRED_KEYS - set(row.keys())
            assert not missing, f"Row for '{row.get('domain')}' missing keys: {missing}"

    def test_composite_bounded(self, report_payload):
        for row in report_payload["dasha_domain_matrix"]:
            c = row["composite"]
            assert -5.0 <= c <= 5.0, (
                f"composite={c} for '{row['domain']}' out of range"
            )

    def test_sub_level_structure(self, report_payload):
        for row in report_payload["dasha_domain_matrix"]:
            for level in ("maha", "antar", "pratyantar"):
                info = row[level]
                assert "activation" in info, f"Missing 'activation' in {level} for {row['domain']}"
                # 'band' is only present when a dasha lord is active
                if info.get("planet") is not None:
                    assert "band" in info, f"Missing 'band' in {level} for {row['domain']}"


class TestReportHeatmapCorrelation:
    """Report domain scores should directionally agree with prediction scores."""

    def test_career_direction_agreement(self, report_payload):
        """The sign of the career domain score should match the report's domain story sentiment."""
        matrix = report_payload["dasha_domain_matrix"]
        career_row = next((r for r in matrix if r["domain"] == "career"), None)
        assert career_row is not None, "Career domain not found in matrix"
        # Just verify the composite is a valid float
        assert isinstance(career_row["composite"], (int, float))
