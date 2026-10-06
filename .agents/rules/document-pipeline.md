# Document Verification Pipeline Rules

## 1. Document Ingestion & Parsers

- Supported document types: `commercial_invoice`, `packing_list`, `shipping_bill`, `purchase_order`, `quality_certificate`.
- Ingestion max size: **20 MB**. Check magic bytes / MIME types, not solely file extensions.
- PDF Text Extraction:
  - Attempt digital text extraction with `pdfplumber` first.
  - If text yield is `< 50` characters per page, automatically fall back to OCR via `pdf2image` + `pytesseract`.
- Image Pre-processing for OCR:
  - Convert to grayscale, apply contrast enhancement and deskewing before running Tesseract.
- Word & Excel documents:
  - Parse `.docx` via `python-docx` extracting paragraphs and table cells.
  - Parse `.xlsx` via `openpyxl` iterating sheets and cell matrices.

---

## 2. LLM Extraction & Canonical Schema

- The system supports dual providers: OpenAI and IBM watsonx, selected by `LLM_PROVIDER`.
- Prompts must require strict JSON formatted output adhering to the canonical field list for the target `doc_type`.
- Canonical fields extracted per document type:
  - **All documents**: `exporter_name`, `product_description`.
  - **Invoice, Packing List, Shipping Bill, PO**: `importer_name`, `shipment_date`, `total_quantity`, `hs_code`.
  - **Invoice, Packing List, Shipping Bill**: `total_weight_kg`.
  - **Invoice & PO**: `total_value_usd`, `currency`.
  - **Specific documents**:
    - Invoice: `invoice_number`, `payment_terms`, `port_of_loading`, `port_of_discharge`.
    - Packing List: `number_of_cartons`, `gross_weight_kg`, `net_weight_kg`.
    - Shipping Bill: `shipping_bill_number`, `vessel_name`, `voyage_number`, `port_of_loading`, `port_of_discharge`.
    - Purchase Order: `po_number`, `buyer_ref`.
    - Quality Cert: `certificate_number`, `lab_name`, `test_date`.

---

## 3. Discrepancy Detection & Normalization

When comparing values between two documents for field $F$:
1. **Numeric Comparison**:
   - Parse numbers removing currency symbols, commas, and unit suffixes.
   - Discrepancy flagged if relative difference $> \text{NUMERIC\_TOLERANCE}$ (default `0.01` / 1%):
     $$\frac{|A - B|}{\max(|A|, |B|)} > \text{NUMERIC\_TOLERANCE}$$
2. **Date Comparison**:
   - Parse dates using `dateutil.parser` or regex into ISO `YYYY-MM-DD`. Compare parsed date objects.
3. **String Comparison**:
   - Normalize strings by stripping whitespace and converting to lowercase.
   - Check semantic equivalence for descriptions or ports where appropriate.
4. **Severity Assignment**:
   - `critical`: `total_quantity`, `total_weight_kg`, `total_value_usd`, `number_of_cartons`, `hs_code`.
   - `warning`: `product_description`, `shipment_date`, `port_of_loading`, `port_of_discharge`, `exporter_name`, `importer_name`.
   - `info`: All remaining fields.

---

## 4. Export Readiness Checklist

The readiness checklist must evaluate 5 distinct verification criteria:
1. All 5 required document types are uploaded for the shipment.
2. All documents completed extraction successfully (`extraction_status == "done"`).
3. Zero open `critical` discrepancies exist.
4. Consistency across core legal fields (`hs_code`, `port_of_loading`, `port_of_discharge`).
5. Consistency across core quantity fields (`total_quantity`, `total_weight_kg`).
