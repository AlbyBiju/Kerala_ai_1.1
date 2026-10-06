"""Generate valid PDF fixture documents for testing the verification pipeline.

Run from backend/ with the project venv:
    .venv/Scripts/python ../scripts/generate_fixtures.py
"""
import os
import pymupdf

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "docs", "fixtures"))

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

SHIPPING_BILL_LINES = [
    "SHIPPING BILL / BILL OF LADING",
    "Shipping Bill Number: SB-2026-44120",
    "Exporter: Apex Global Agro Exports Ltd.",
    "Importer: Pacific Rim Imports Pte Ltd",
    "Date: 2026-10-06",
    "Total Quantity: 1200 Cartons",
    "Total Weight: 14400 KG",
    "HS Code: 0306.17.00",
    "Product Description: Frozen Vannamei Shrimps",
    "Port of Loading: Cochin Port, India",
    "Port of Discharge: Port of Singapore",
    "Vessel Name: MV Ocean Trader",
    "Voyage Number: V-221",
]

PURCHASE_ORDER_LINES = [
    "PURCHASE ORDER",
    "PO Number: PO-2026-9041",
    "Buyer Ref: PACIFIC-RIM-PO-881",
    "Exporter: Apex Global Agro Exports Ltd.",
    "Importer: Pacific Rim Imports Pte Ltd",
    "Date: 2026-10-06",
    "Total Quantity: 1200 Cartons",
    "Total Value: 68400 USD",
    "HS Code: 0306.17.00",
    "Product Description: Frozen Vannamei Shrimps",
    "Payment Terms: Letter of Credit at sight",
]

QUALITY_CERT_LINES = [
    "CERTIFICATE OF QUALITY & INSPECTION",
    "Certificate Number: QC-AGRO-2026-114",
    "Exporter: Apex Global Agro Exports Ltd.",
    "Product Description: Frozen Vannamei Shrimps",
    "Lab Name: SGS Marine & Agro Laboratories",
    "Date: 2026-10-06",
    "Standard: Grade A Frozen Seafood Export Compliance",
]


def make_pdf(filename: str, lines: list[str]) -> None:
    doc = pymupdf.open()
    page = doc.new_page()
    rect = pymupdf.Rect(72, 72, 523, 770)
    page.insert_textbox(rect, "\n".join(lines), fontsize=11, fontname="helv")
    path = os.path.join(OUT_DIR, filename)
    doc.save(path)
    doc.close()
    print(f"Created {path}")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    make_pdf("invoice.pdf", INVOICE_LINES)
    make_pdf("packing_list.pdf", PACKING_LIST_LINES)
    make_pdf("shipping_bill.pdf", SHIPPING_BILL_LINES)
    make_pdf("purchase_order.pdf", PURCHASE_ORDER_LINES)
    make_pdf("quality_certificate.pdf", QUALITY_CERT_LINES)
