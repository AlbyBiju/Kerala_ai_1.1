# Architecture — Export Document Verification System

## Overview

The system is a single-team web application composed of three primary tiers:

1. **Frontend** — React SPA served by nginx
2. **Backend** — Python FastAPI REST API
3. **Database** — PostgreSQL

Supporting services:
- **OCR Engine** — Tesseract (via pytesseract + pdf2image)
- **AI Extraction** — IBM watsonx or OpenAI (switchable via env var)
- **PDF Generator** — WeasyPrint + Jinja2 templates
- **Background Tasks** — FastAPI BackgroundTasks (MVP); Celery + Redis (production option)

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                              │
│              React + Vite + TailwindCSS                     │
│   (Login · Dashboard · Shipments · Discrepancy Review)      │
└────────────────────────┬────────────────────────────────────┘
                         │  HTTPS  REST/JSON  JWT Bearer
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                             │
│  ┌──────────┐  ┌────────────┐  ┌──────────────────────┐    │
│  │ Auth API │  │Shipment API│  │  Discrepancy/Report  │    │
│  │/auth/... │  │/shipments/ │  │  API  /discrepancies │    │
│  └──────────┘  └────────────┘  └──────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Background Task Runner                  │   │
│  │   FastAPI BackgroundTasks  (or Celery + Redis)       │   │
│  │                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │   │
│  │  │ Parsing Layer│  │AI Extraction │  │Discrepancy│  │   │
│  │  │  (OCR/PDF/   │→ │  Service     │→ │ Engine   │  │   │
│  │  │  DOCX/XLSX)  │  │(OpenAI/wx)   │  │+ Checklist│  │   │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │Storage Service│  │Report Service│                        │
│  │(local / S3)  │  │(WeasyPrint)  │                        │
│  └──────────────┘  └──────────────┘                        │
└────────────────────────┬────────────────────────────────────┘
                         │  SQLAlchemy async (asyncpg)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     PostgreSQL                               │
│                                                             │
│  shipment_sessions  documents  extracted_fields             │
│  discrepancies      checklist_items                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Repository Layout

```
/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers
│   │   │   ├── auth.py
│   │   │   └── shipments.py
│   │   ├── core/             # Config, DB engine, security, deps
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── deps.py
│   │   │   └── security.py
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── shipment.py
│   │   │   ├── document.py
│   │   │   ├── extracted_field.py
│   │   │   ├── discrepancy.py
│   │   │   └── checklist_item.py
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic
│   │   │   ├── storage.py
│   │   │   ├── llm.py
│   │   │   ├── extraction.py
│   │   │   ├── discrepancy.py
│   │   │   └── report.py
│   │   ├── tasks/            # Background task orchestration
│   │   │   └── process_document.py
│   │   ├── templates/        # Jinja2 HTML templates for PDF
│   │   │   └── report.html
│   │   └── utils/
│   │       └── parsers.py    # OCR + document parsing
│   ├── alembic/              # DB migrations
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── context/          # AuthContext
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Route-level page components
│   │   ├── lib/              # Axios instance, helpers
│   │   └── main.tsx
│   ├── public/
│   ├── Dockerfile
│   └── vite.config.ts
│
├── docs/
│   └── fixtures/             # Sample documents for testing
│
├── scripts/                  # Dev/ops utility scripts
├── docker-compose.yml        # Local dev (PostgreSQL + pgAdmin)
├── docker-compose.prod.yml   # Production compose
├── ARCHITECTURE.md           # This file
├── REFERENCE.md              # API & field reference
├── TASKS.md                  # Detailed task breakdown
├── CHANGELOG.md              # Version history
├── CONTRIBUTING.md           # Contribution guide
└── README.md                 # Setup & usage
```

---

## Data Flow

### Document Upload & Processing

```
User uploads file
      │
      ▼
POST /shipments/{id}/documents
      │  validates MIME type & size
      │  saves to UPLOAD_DIR via StorageService
      │  creates Document record (status: pending)
      │  returns 202 Accepted
      │
      ▼ (background task)
parse_document(path, mime_type)
      │  → pdfplumber / Tesseract OCR / python-docx / openpyxl
      │  → returns ParsedDocument
      │
      ▼
ExtractionService.extract(parsed_doc, doc_type)
      │  → builds structured prompt
      │  → calls LLM (OpenAI / watsonx)
      │  → parses JSON response
      │  → saves ExtractedField rows
      │  → updates Document.extraction_status = done
      │
      ▼ (if all session documents are done)
DiscrepancyEngine.run(shipment_id)
      │  → compares extracted fields across document pairs
      │  → saves Discrepancy records
      │  → generates ChecklistItem records
      │  → updates ShipmentSession.status = reviewed
```

### Report Generation

```
GET /shipments/{id}/report/pdf
      │
      ▼
ReportService.generate_pdf_report(shipment_id)
      │  → queries shipment, documents, discrepancies, checklist
      │  → renders report.html via Jinja2
      │  → converts HTML → PDF via WeasyPrint
      │  → streams bytes to client
```

---

## Database Schema

```
shipment_sessions
  id            UUID PK
  name          TEXT
  description   TEXT
  status        ENUM (draft/processing/reviewed/closed)
  created_at    TIMESTAMP
  updated_at    TIMESTAMP

documents
  id                UUID PK
  shipment_id       UUID FK → shipment_sessions
  doc_type          ENUM (commercial_invoice/packing_list/shipping_bill/
                          purchase_order/quality_certificate)
  original_filename TEXT
  storage_path      TEXT
  mime_type         TEXT
  extraction_status ENUM (pending/processing/done/failed)
  created_at        TIMESTAMP

extracted_fields
  id               UUID PK
  document_id      UUID FK → documents
  field_name       TEXT
  field_value      TEXT
  confidence_score FLOAT
  page_number      INT

discrepancies
  id               UUID PK
  shipment_id      UUID FK → shipment_sessions
  field_name       TEXT
  document_a_id    UUID FK → documents
  document_a_value TEXT
  document_b_id    UUID FK → documents
  document_b_value TEXT
  severity         ENUM (critical/warning/info)
  status           ENUM (open/acknowledged/resolved)
  created_at       TIMESTAMP

checklist_items
  id          UUID PK
  shipment_id UUID FK → shipment_sessions
  label       TEXT
  is_passed   BOOLEAN
  notes       TEXT
```

---

## Authentication

Single-team shared login. No user accounts or roles.

- Credentials (`TEAM_USERNAME`, `TEAM_PASSWORD`) are stored in the server `.env` file.
- `POST /auth/login` validates credentials and returns a signed JWT.
- All other endpoints require `Authorization: Bearer <token>`.
- Token expiry is configurable via `JWT_EXPIRE_MINUTES` (default: 480 — 8 hours).

---

## LLM Provider Abstraction

```
LLMProvider (Protocol)
    └── complete(prompt: str, schema: dict) -> dict

OpenAIProvider      ← selected when LLM_PROVIDER=openai
WatsonxProvider     ← selected when LLM_PROVIDER=watsonx
```

The provider is instantiated once at startup in `app/services/llm.py` and injected into
`ExtractionService`. Switching providers requires only an env var change — no code changes.

---

## Key Technical Decisions

| Decision | Choice | Reason |
|---|---|---|
| Async ORM | SQLAlchemy 2.x async + asyncpg | Non-blocking DB queries under load |
| Background tasks | FastAPI BackgroundTasks (MVP) | Zero extra infrastructure for MVP |
| OCR fallback | Auto-detect low-yield PDFs | Handles both native and scanned PDFs transparently |
| PDF generation | WeasyPrint + Jinja2 HTML | Easier to style than low-level PDF libs |
| Numeric tolerance | ±1% configurable | Avoids false positives from rounding differences |
| File storage | Local filesystem with S3-ready interface | Simple MVP; swap without logic changes |
