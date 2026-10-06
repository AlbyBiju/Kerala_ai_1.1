---
name: exportguard-pipeline
description: >-
  Use this skill when developing, testing, or debugging the document ingestion, OCR parsing, LLM extraction, discrepancy engine, or PDF reporting pipeline for ExportGuard.
---

# ExportGuard Document Verification Pipeline Skill

This skill guides the implementation, testing, and debugging of the core ExportGuard verification pipeline (Sub-Tasks 4 through 8).

---

## 1. Pipeline Stages

```
Uploaded Document
      │
      ▼
1. Storage Service (save file to disk / S3 abstraction)
      │
      ▼
2. Parsers Dispatcher (pdfplumber / Tesseract OCR / docx / xlsx)
      │
      ▼
3. AI Extraction Service (OpenAI / Watsonx structured JSON prompts)
      │
      ▼
4. ExtractedField Persistence (SQLAlchemy async)
      │
      ▼
5. Discrepancy Detection Engine (pairwise field comparison + severity rating)
      │
      ▼
6. Export Readiness Checklist (5 validation rules)
      │
      ▼
7. Report Service (Jinja2 template + WeasyPrint PDF generation)
```

---

## 2. Ingestion & Parser Procedures

1. **Dispatcher Logic (`app/utils/parsers.py`)**:
   - Inspect MIME type and magic bytes.
   - For `application/pdf`:
     - Extract text with `pdfplumber`.
     - Count total characters. If avg characters/page < 50, route to OCR fallback.
   - For images (`image/png`, `image/jpeg`, `image/tiff`):
     - Load via Pillow (`PIL.Image`).
     - Preprocess: Convert to grayscale, enhance contrast, deskew.
     - Call `pytesseract.image_to_string(image, lang=settings.OCR_LANG)`.
   - For `application/vnd.openxmlformats-officedocument.wordprocessingml.document`:
     - Extract paragraphs and tables using `python-docx`.
   - For `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`:
     - Extract worksheets and cells using `openpyxl`.

---

## 3. LLM Extraction Implementation

1. **Provider Factory (`app/services/llm.py`)**:
   - Define `LLMProvider` Protocol with `async def generate_json(prompt: str, schema: dict) -> dict`.
   - Implement `OpenAIProvider` using `openai.AsyncOpenAI` with `response_format={"type": "json_object"}`.
   - Implement `WatsonxProvider` using `ibm-watsonx-ai` SDK.
   - Factory function `get_llm_provider()` switches based on `settings.LLM_PROVIDER`.

2. **Prompt Strategy (`app/services/extraction.py`)**:
   - Provide the document text and the list of expected canonical fields for that document type.
   - Prompt instructions must request exact field extractions with confidence scores and page numbers.
   - Validate response against Pydantic schema before persisting `ExtractedField` rows.

---

## 4. Discrepancy Detection Algorithm

1. **Field Comparison (`app/services/discrepancy.py`)**:
   - **Numeric fields** (`total_quantity`, `total_weight_kg`, `total_value_usd`, `number_of_cartons`, `gross_weight_kg`, `net_weight_kg`):
     - Strip symbols and parse float.
     - If $|A - B| / \max(|A|, |B|) > \text{NUMERIC\_TOLERANCE}$ (0.01), flag discrepancy.
   - **Dates** (`shipment_date`, `test_date`):
     - Parse to standard ISO `YYYY-MM-DD` and check equality.
   - **Strings** (`hs_code`, `exporter_name`, `importer_name`, `product_description`, `port_of_loading`, `port_of_discharge`):
     - Clean, strip whitespace, lowercase, and compare.
2. **Severity Mapping**:
   - `critical`: Legal and customs blockers (`total_quantity`, `total_weight_kg`, `total_value_usd`, `number_of_cartons`, `hs_code`).
   - `warning`: Commercial discrepancies (`product_description`, `shipment_date`, `port_of_loading`, `port_of_discharge`, `exporter_name`, `importer_name`).
   - `info`: Non-critical fields.

---

## 5. Checklist Rules

Evaluate and produce 5 `ChecklistItem` records:
1. Complete document package (all 5 doc types present).
2. Extraction success (no documents with `failed` status).
3. Zero critical discrepancies.
4. Port and HS code consistency.
5. Quantity and weight consistency.
