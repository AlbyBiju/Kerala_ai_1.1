# Export Document Verification System — Plan

## Top-Level Overview

Build a single-team web application that allows a documentation team to upload export documents
(PDF, images, Word, Excel, and scanned documents via OCR), automatically extract structured data
using AI (IBM watsonx or OpenAI), compare fields across documents within a shipment session, flag
discrepancies, and generate an export-readiness checklist and a downloadable PDF summary report.

**Stack:**
- **Frontend:** React (Vite), TailwindCSS, React Query, React Router
- **Backend:** Python / FastAPI
- **Database:** PostgreSQL (via SQLAlchemy ORM + Alembic migrations)
- **AI Extraction:** IBM watsonx or OpenAI (structured extraction prompts)
- **OCR:** Tesseract OCR (via pytesseract) for scanned image inputs; pdf2image for PDF-to-image
- **Document Parsing:** python-docx (Word), openpyxl (Excel), pdfplumber (native PDF)
- **PDF Report Generation:** WeasyPrint + Jinja2
- **Auth:** Single shared login (username + password, JWT session token) — no RBAC, no roles
- **File Storage:** Local filesystem (MVP) with an abstraction layer ready for S3

**Scope (MVP):**
- Single login for the entire team (shared credentials)
- Upload and parse 5 document types: Commercial Invoice, Packing List, Shipping Bill,
  Purchase Order, Quality Certificate
- AI-powered structured data extraction
- Field-level comparison and discrepancy detection
- Export readiness checklist
- Summary dashboard
- PDF report download
- Persistent shipment sessions with history

**Out of scope:**
- Multi-user accounts, roles, or per-user permissions
- User management / admin panel
- Audit trails per individual user

## Supporting Documentation

| File | Purpose |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System design, data flow diagrams, DB schema, directory layout |
| [`REFERENCE.md`](REFERENCE.md) | Full REST API reference, canonical field schema, env var reference |
| [`TASKS.md`](TASKS.md) | Authoritative granular task checklist — update statuses here during implementation |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history — update under [Unreleased] as sub-tasks complete |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Dev setup, code style, branch strategy, PR checklist |

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffolding & Repository Structure

**Status:** `[ ] pending`

**Intent:**
Establish the mono-repo folder structure, tooling configuration, and environment setup so all
subsequent sub-tasks build on a consistent foundation.

**Expected Outcomes:**
- `/backend` FastAPI project with virtual environment, dependencies, and folder layout
- `/frontend` React (Vite) project with TailwindCSS configured
- `docker-compose.yml` for local PostgreSQL
- `.env.example` files for backend and frontend
- `README.md` with setup instructions

**Todo List:**
1. Create root directory layout: `/backend`, `/frontend`, `/docs`, `/scripts`
2. Scaffold FastAPI project inside `/backend`: `main.py`, `app/` package with `api/`, `core/`,
   `models/`, `schemas/`, `services/`, `utils/`, `tasks/`, `templates/`
3. Add `backend/requirements.txt`: fastapi, uvicorn, sqlalchemy, alembic, asyncpg, python-jose,
   passlib, python-multipart, pytesseract, pdf2image, pdfplumber, python-docx, openpyxl,
   openai, pillow, weasyprint, jinja2, httpx, pydantic-settings
4. Scaffold React + Vite project inside `/frontend` with TailwindCSS, React Router, React Query,
   Axios, React Hook Form, react-hot-toast, Recharts
5. Add `docker-compose.yml` for PostgreSQL + pgAdmin
6. Add `backend/.env.example` (see full var list in `REFERENCE.md`)
7. Add `frontend/.env.example` with `VITE_API_BASE_URL`
8. Write root `README.md` with local setup steps, system dependency notes

**Relevant Context:**
- Greenfield project — no existing code
- Storage abstraction lives in `backend/app/services/storage.py`
- System dependencies (tesseract, poppler, cairo) — see `CONTRIBUTING.md` for install commands

---

### Sub-Task 2 — Database Models & Migrations

**Status:** `[ ] pending`

**Intent:**
Define all database tables and generate Alembic migrations. Because this is single-team, there
is no `users` table — sessions and documents are not tied to any user identity.

**Expected Outcomes:**
- All ORM models created and migratable with no user/role tables
- Alembic configured with initial migration
- Relationships between models verified

**Todo List:**
1. Configure SQLAlchemy async engine and session factory in `app/core/database.py`
2. Create `app/core/config.py` using pydantic-settings to load all env vars
3. Create `app/models/shipment.py`: `ShipmentSession` — id, name, description,
   status (enum: draft/processing/reviewed/closed), created_at, updated_at
4. Create `app/models/document.py`: `Document` — id, shipment_id (FK), doc_type
   (enum: commercial_invoice/packing_list/shipping_bill/purchase_order/quality_certificate),
   original_filename, storage_path, mime_type,
   extraction_status (enum: pending/processing/done/failed), created_at
5. Create `app/models/extracted_field.py`: `ExtractedField` — id, document_id (FK),
   field_name, field_value, confidence_score, page_number
6. Create `app/models/discrepancy.py`: `Discrepancy` — id, shipment_id (FK), field_name,
   document_a_id (FK), document_a_value, document_b_id (FK), document_b_value,
   severity (enum: critical/warning/info), status (enum: open/acknowledged/resolved), created_at
7. Create `app/models/checklist_item.py`: `ChecklistItem` — id, shipment_id (FK), label,
   is_passed, notes
8. Export all models from `app/models/__init__.py` for Alembic auto-detect
9. Run `alembic init alembic` and configure `alembic.ini` and `alembic/env.py` for async engine
10. Generate initial migration and verify it applies cleanly

**Relevant Context:**
- DB schema diagram in `ARCHITECTURE.md` → Database Schema section
- No `User` model — simplifies schema significantly
- Async SQLAlchemy requires `asyncpg` driver

---

### Sub-Task 3 — Single-Team Authentication

**Status:** `[ ] pending`

**Intent:**
Implement a minimal login gate: one shared username + password stored in environment variables,
returning a JWT session token. No registration, no user management.

**Expected Outcomes:**
- `POST /auth/login` validates credentials against env vars and returns a JWT
- `get_current_session` FastAPI dependency validates JWT on protected routes
- All other endpoints require a valid token
- Token expiry configurable via `JWT_EXPIRE_MINUTES`

**Todo List:**
1. Create `app/core/security.py`: `verify_password()`, `create_access_token()`,
   `decode_access_token()`
2. Create `app/schemas/auth.py`: `LoginRequest`, `TokenResponse`
3. Create `app/api/auth.py`: `POST /auth/login` router only — no register endpoint
4. Create `app/core/deps.py`: `get_current_session` dependency (validates JWT Bearer token,
   raises 401 if missing or invalid)
5. Write unit tests in `backend/tests/test_auth.py`

**Relevant Context:**
- API contract in `REFERENCE.md` → Authentication section
- Credentials loaded from `TEAM_USERNAME` / `TEAM_PASSWORD` env vars via `app/core/config.py`
- All subsequent API routers use `Depends(get_current_session)`

---

### Sub-Task 4 — Document Upload & File Storage Service

**Status:** `[ ] pending`

**Intent:**
Allow the team to upload documents into a shipment session. Files are validated, stored, and a
database record is created. The storage service is abstracted for future S3 compatibility.

**Expected Outcomes:**
- `POST /shipments/{id}/documents` accepts multipart file upload
- Supported MIME types validated: PDF, PNG, JPEG, TIFF, DOCX, XLSX
- File saved to configurable `UPLOAD_DIR`
- `Document` record created in DB with status `pending`
- 20 MB file size limit enforced

**Todo List:**
1. Create `app/services/storage.py`: `StorageService.save_file()` and `delete_file()`
2. Create `app/schemas/document.py`: `DocumentOut`, `DocumentUploadResponse`,
   `ShipmentOut`, `ShipmentCreate`
3. Create `app/api/shipments.py` with all shipment and document endpoints
4. Validate MIME type from file content headers (not just extension)
5. Enforce 20 MB limit via FastAPI settings
6. Write integration tests in `backend/tests/test_upload.py`

**Relevant Context:**
- Full endpoint specs in `REFERENCE.md` → Shipment Sessions section
- Supported MIME types table in `REFERENCE.md` → Supported File Formats section
- `Document` model from Sub-Task 2

---

### Sub-Task 5 — OCR & Document Parsing Pipeline

**Status:** `[ ] pending`

**Intent:**
Build the raw text and table extraction layer that converts every supported file format into a
normalised `ParsedDocument` intermediate representation before AI extraction.

**Expected Outcomes:**
- `parse_document(storage_path, mime_type) -> ParsedDocument` handles all 6 input formats
- Scanned PDFs and images run through Tesseract OCR with image pre-processing
- Native PDFs use pdfplumber; fallback to OCR when text yield is too low
- DOCX/XLSX parsed with python-docx / openpyxl
- Stable `ParsedDocument` dataclass consumed by the AI extraction service

**Todo List:**
1. Define `ParsedDocument` dataclass in `app/utils/parsers.py`:
   `raw_text: str`, `tables: list[list[list[str]]]`, `pages: int`, `source_type: str`
2. Implement `parse_pdf(path)`: pdfplumber + OCR fallback (threshold: 50 chars/page)
3. Implement `parse_image(path)`: Pillow pre-processing (grayscale, deskew, contrast) + Tesseract
4. Implement `parse_docx(path)`: python-docx paragraphs and tables
5. Implement `parse_xlsx(path)`: openpyxl cell iteration across all sheets
6. Implement `parse_document(path, mime_type)` dispatcher
7. Add OCR language config from `OCR_LANG` env var
8. Add sample fixture files to `docs/fixtures/` for testing
9. Write unit tests per parser in `backend/tests/test_parsers.py`

**Relevant Context:**
- System binary install instructions in `CONTRIBUTING.md`
- `ParsedDocument` is the contract between Sub-Tasks 5 and 6

---

### Sub-Task 6 — AI-Powered Structured Data Extraction

**Status:** `[ ] pending`

**Intent:**
Use an LLM to extract structured, field-level data from `ParsedDocument` output into a canonical
field schema, then persist it so the discrepancy engine can compare across documents.

**Expected Outcomes:**
- `ExtractionService.extract(parsed_doc, doc_type) -> list[ExtractedField]` for all 5 doc types
- Canonical field schema defined in `app/core/fields.py`
- Extracted fields saved to `extracted_fields` table with confidence scores
- `Document.extraction_status` updated to `done` or `failed`
- Switchable LLM provider via `LLM_PROVIDER` env var

**Todo List:**
1. Define canonical field schema and severity map in `app/core/fields.py`
2. Create `app/services/llm.py`: `LLMProvider` protocol, `OpenAIProvider`, `WatsonxProvider`,
   `get_llm_provider()` factory
3. Create `app/services/extraction.py`: `ExtractionService.extract()` with per-doc-type
   structured JSON prompts; use JSON mode / function calling for structured output
4. Persist `ExtractedField` rows to DB
5. Update `Document.extraction_status` after extraction
6. Write tests with mocked LLM in `backend/tests/test_extraction.py`

**Relevant Context:**
- Full canonical field table in `REFERENCE.md` → Canonical Field Schema section
- LLM provider env vars in `REFERENCE.md` → Environment Variables section
- Guide for adding a new provider in `CONTRIBUTING.md`

---

### Sub-Task 7 — Discrepancy Detection Engine

**Status:** `[ ] pending`

**Intent:**
Compare extracted fields across all documents in a shipment session and produce a structured list
of discrepancies. Generate the export readiness checklist from the results.

**Expected Outcomes:**
- `DiscrepancyEngine.run(shipment_id)` compares all document pairs on shared canonical fields
- Numeric fields use ±1% tolerance (configurable via `NUMERIC_TOLERANCE` env var)
- String fields normalised (lowercase, stripped); dates parsed before comparison
- Severity auto-assigned from field severity map in `app/core/fields.py`
- Results saved to `discrepancies` and `checklist_items` tables

**Todo List:**
1. Create `app/services/discrepancy.py`: `DiscrepancyEngine` class
2. Implement `compare_fields(field_name, value_a, value_b) -> Discrepancy | None`
3. Implement severity assignment using map from `app/core/fields.py`
4. Implement `DiscrepancyEngine.run(shipment_id)` — iterate document pairs, persist results
5. Implement `generate_checklist(shipment_id) -> list[ChecklistItem]`
6. Persist `ChecklistItem` records
7. Add `POST /shipments/{id}/analyse` endpoint (202, background task)
8. Write tests in `backend/tests/test_discrepancy.py`

**Relevant Context:**
- Severity rules table in `REFERENCE.md` → Severity Rules section
- `Discrepancy` and `ChecklistItem` models from Sub-Task 2

---

### Sub-Task 8 — REST API — Reports & Dashboard Endpoints

**Status:** `[ ] pending`

**Intent:**
Expose discrepancy data, checklist, summary statistics, and PDF report download via REST endpoints.

**Expected Outcomes:**
- `GET /shipments/{id}/discrepancies` returns discrepancies with severity/status filters
- `PATCH /shipments/{id}/discrepancies/{disc_id}` updates discrepancy status
- `GET /shipments/{id}/checklist` returns checklist items
- `GET /shipments/{id}/report/pdf` streams a PDF summary report
- `GET /dashboard` returns aggregate stats

**Todo List:**
1. Add discrepancy list and status-update routes to `app/api/shipments.py`
2. Add checklist route
3. Create `app/services/report.py`: `generate_pdf_report(shipment_id, db) -> bytes`
4. Create `app/templates/report.html`: Jinja2 template with severity colour coding
5. Add `GET /shipments/{id}/report/pdf` streaming endpoint
6. Create `app/api/dashboard.py` with `GET /dashboard`
7. Write endpoint tests in `backend/tests/test_reports.py`

**Relevant Context:**
- Full endpoint specs in `REFERENCE.md` → REST API Reference section
- Dashboard response schema in `REFERENCE.md` → Dashboard section
- WeasyPrint system dep install in `CONTRIBUTING.md`

---

### Sub-Task 9 — Background Task Processing

**Status:** `[ ] pending`

**Intent:**
Move the parse → extract → analyse pipeline to background tasks so uploads return immediately
and large/scanned documents do not cause HTTP timeouts.

**Expected Outcomes:**
- Upload endpoint returns `202 Accepted` immediately
- Extraction and analysis run asynchronously
- Document and shipment status updated as tasks progress
- Frontend polling reflects live status

**Todo List:**
1. Create `app/tasks/process_document.py`: parse → extract → auto-trigger analyse when all done
2. Refactor upload endpoint to use FastAPI `BackgroundTasks`
3. Refactor analyse endpoint to run as background task
4. Add optional Celery wiring in `app/core/worker.py` (`TASK_BACKEND=celery` env var)
5. Write tests in `backend/tests/test_tasks.py`

**Relevant Context:**
- `TASK_BACKEND` and `CELERY_BROKER_URL` env vars documented in `REFERENCE.md`
- FastAPI `BackgroundTasks` is sufficient for MVP

---

### Sub-Task 10 — Frontend: App Shell, Auth & Routing

**Status:** `[ ] pending`

**Intent:**
Build the React application shell with routing, a login page, and a JWT-injecting API client.

**Expected Outcomes:**
- Login page functional against the backend
- JWT stored in localStorage, attached to all API requests
- Protected routes redirect unauthenticated users to login
- Responsive sidebar layout

**Todo List:**
1. Configure Axios instance in `src/lib/api.ts` with JWT interceptors
2. Create `src/context/AuthContext.tsx`: `isLoggedIn`, `login()`, `logout()`
3. Create `src/pages/Login.tsx` with React Hook Form
4. Create `src/components/ProtectedRoute.tsx`
5. Set up React Router: `/login`, `/dashboard`, `/shipments`, `/shipments/:id`,
   `/shipments/:id/report`
6. Create `src/components/AppLayout.tsx` with sidebar
7. Configure React Query `QueryClient` in `src/main.tsx`

**Relevant Context:**
- No register page — single shared login
- Auth API contract in `REFERENCE.md` → Authentication section

---

### Sub-Task 11 — Frontend: Shipment Sessions & Document Upload UI

**Status:** `[ ] pending`

**Intent:**
Build the shipment session management pages and multi-document upload interface.

**Expected Outcomes:**
- Shipments list with status badges and create modal
- Document upload with doc-type selector, drag-and-drop, progress indicator
- Extraction status polled until all documents finish

**Todo List:**
1. Create `src/pages/Shipments.tsx`
2. Create `src/components/CreateShipmentModal.tsx`
3. Create `src/pages/ShipmentDetail.tsx` with document list and "Run Analysis" button
4. Create `src/components/DocumentUpload.tsx` with drag-and-drop and progress bar
5. Implement React Query polling (`refetchInterval: 3000`)
6. Add react-hot-toast notifications

---

### Sub-Task 12 — Frontend: Discrepancy Review & Checklist UI

**Status:** `[ ] pending`

**Intent:**
Build the core discrepancy review interface — the primary value screen of the application.

**Expected Outcomes:**
- Discrepancies grouped by severity with colour coding
- Inline status change with optimistic update
- Export readiness checklist with overall readiness score

**Todo List:**
1. Create `src/pages/DiscrepancyReview.tsx`
2. Create `src/components/DiscrepancyCard.tsx` with severity badge and status dropdown
3. Implement optimistic update via React Query mutation
4. Create `src/components/ChecklistPanel.tsx` with pass/fail cards
5. Add readiness score progress bar

---

### Sub-Task 13 — Frontend: Dashboard & PDF Report Download

**Status:** `[ ] pending`

**Intent:**
Build the summary dashboard and PDF report download flow.

**Expected Outcomes:**
- Dashboard with stat cards, recent sessions table, donut chart
- PDF download button triggers browser file download

**Todo List:**
1. Create `src/pages/Dashboard.tsx` with stat cards and Recharts donut chart
2. Add "Download Report" button on `ShipmentDetail.tsx` (blob download)
3. Handle loading and error states for all queries

---

### Sub-Task 14 — End-to-End Testing, Containerisation & Documentation

**Status:** `[ ] pending`

**Intent:**
Validate the full pipeline end-to-end, containerise the application, and finalise documentation.

**Expected Outcomes:**
- E2E test: upload Invoice + Packing List with known 1,200 vs 1,180 carton discrepancy
  → analyse → discrepancy detected → PDF downloaded
- Dockerfiles for backend and frontend
- `docker-compose.prod.yml` wiring all services
- README finalised

**Todo List:**
1. Create fixture documents in `docs/fixtures/`
2. Write E2E test in `backend/tests/test_e2e.py`
3. Write `backend/Dockerfile` (Python slim + tesseract + poppler + cairo)
4. Write `frontend/Dockerfile` (Node build + nginx serve)
5. Write `docker-compose.prod.yml`
6. Add nginx `/api` proxy config
7. Update `README.md` with Docker deployment section
8. Run full test suite — all green
9. Update `CHANGELOG.md` with v0.1.0 release notes

**Relevant Context:**
- Docker image system deps in `CONTRIBUTING.md`
- All env vars documented in `REFERENCE.md`
