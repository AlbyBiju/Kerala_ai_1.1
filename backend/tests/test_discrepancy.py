import pytest
from app.services.discrepancy import compare_values
from app.core.fields import get_field_severity

def test_numeric_comparison_within_tolerance():
    # 1000 vs 1005 (0.5% diff <= 1% tolerance) -> should match (True)
    assert compare_values("total_quantity", "1000", "1005") is True

def test_numeric_comparison_exceeding_tolerance():
    # 1000 vs 1025 (2.5% diff > 1% tolerance) -> should discrepancy (False)
    assert compare_values("total_quantity", "1000", "1025") is False

def test_date_comparison_different_formats():
    # 2026-10-06 vs 06/10/2026 or Oct 6, 2026 -> should match
    assert compare_values("shipment_date", "2026-10-06", "October 6, 2026") is True
    assert compare_values("shipment_date", "2026-10-06", "2026-10-07") is False

def test_string_comparison_whitespace_and_casing():
    assert compare_values("exporter_name", "Apex Global Agro Ltd. ", "apex global agro ltd.") is True
    assert compare_values("product_description", "Frozen Shrimps", "Fresh Mangoes") is False

def test_field_severity_classification():
    assert get_field_severity("total_quantity") == "critical"
    assert get_field_severity("total_value_usd") == "critical"
    assert get_field_severity("hs_code") == "critical"
    assert get_field_severity("product_description") == "warning"
    assert get_field_severity("port_of_loading") == "warning"
    assert get_field_severity("invoice_number") == "info"
    assert get_field_severity("certificate_number") == "info"
