"""Shared pytest fixtures: ensure valid PDF test documents exist in docs/fixtures."""
import os
import pytest

FIXTURE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "docs", "fixtures")
)

INVOICE_LINES = [
    "COMMERCIAL INVOICE",
    "Invoice Number: INV-2026-8891",
    "Exporter: Apex Global Agro Exports Ltd.",
    "Importer: Pacific Rim Imports Pte Ltd",
    "Date: 2026-10-06",
    "Total Quantity: 1200 Cartons",
    "Total Weight: 14400 KG",
    "Total Value: 68400 USD",
    "HS Code: 0306.17.00",
    "Product Description: Frozen Vannamei Shrimps",
    "Port of Loading: Cochin Port, India",
    "Port of Discharge: Port of Singapore",
]

PACKING_LIST_LINES = [
    "PACKING LIST",
    "Exporter: Apex Global Agro Exports Ltd.",
    "Importer: Pacific Rim Imports Pte Ltd",
    "Shipment Date: 2026-10-06",
    "Total Quantity: 1180 Cartons",
    "Number of Cartons: 1180",
    "Gross Weight: 14400 KG",
    "Net Weight: 13800 KG",
    "HS Code: 0306.17.00",
    "Product Description: Frozen Vannamei Shrimps",
]


def _make_pdf(path: str, lines: list) -> None:
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    rect = pymupdf.Rect(72, 72, 523, 770)
    page.insert_textbox(rect, "\n".join(lines), fontsize=11, fontname="helv")
    doc.save(path)
    doc.close()


@pytest.fixture(scope="session")
def fixture_dir() -> str:
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    invoice = os.path.join(FIXTURE_DIR, "invoice.pdf")
    packing = os.path.join(FIXTURE_DIR, "packing_list.pdf")
    if not os.path.exists(invoice):
        _make_pdf(invoice, INVOICE_LINES)
    if not os.path.exists(packing):
        _make_pdf(packing, PACKING_LIST_LINES)
    return FIXTURE_DIR


@pytest.fixture(scope="session")
def invoice_pdf_path(fixture_dir: str) -> str:
    return os.path.join(fixture_dir, "invoice.pdf")


@pytest.fixture(scope="session")
def packing_list_pdf_path(fixture_dir: str) -> str:
    return os.path.join(fixture_dir, "packing_list.pdf")
