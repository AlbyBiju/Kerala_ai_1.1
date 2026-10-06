# Tasks — Export Document Verification System

This file is the authoritative task list for building the system. Each sub-task maps to a
discrete, independently implementable unit of work. Tasks must be completed in order — each
sub-task depends on the ones above it.

See `ARCHITECTURE.md` for system design context and `REFERENCE.md` for API and field schemas.
See `export-doc-verification-plan.md` for full intent and expected outcomes per task.

---

## Status Legend

| Symbol | Meaning |
|---|---|
| `[ ]` | Pending |
| `[-]` | In progress |
| `[x]` | Complete |
| `[!]` | Blocked |

---

## Sub-Task 1 — Project Scaffolding & Repository Structure

**Status:** `[ ] pending`

- [ ] Create root directory layout: `/backend`, `/frontend`, `/docs`, `/scripts`
- [ ] Scaffold FastAPI project inside `/backend` with `main.py` and `app/` package
- [ ] Create `app/` sub-packages: `api/`, `core/`, `models/`, `schemas/`, `services/`, `utils/`, `tasks/`, `templates/`
- [ ] Add `backend/requirements.txt` with all dependencies
- [ ] Scaffold React + Vite + TailwindCSS project inside `/frontend`
- [ ] Install frontend dependencies: React Router, React Query, Axios, React Hook Form, react-hot-toast, Recharts
- [ ] Add `docker-compose.yml` for PostgreSQL + pgAdmin (local dev)
- [ ] Add `backend/.env.example` with all backend env vars
- [ ] Add `frontend/.env.example` with `VITE_API_BASE_URL`
- [ ] Write root `README.md` with local setup steps and system dependency notes

---

## Sub-Task 2 — Database Models & Migrations

**Status:** `[ ] pending`

- [ ] Configure SQLAlchemy async engine and session factory in `app/core/database.py`
- [ ] Create `app/core/config.py` using pydantic-settings to load env vars
- [ ] Create `app/models/shipment.py`: `ShipmentSession` model
- [ ] Create `app/models/document.py`: `Document` model
- [ ] Create `app/models/extracted_field.py`: `ExtractedField` model
- [ ] Create `app/models/discrepancy.py`: `Discrepancy` model
- [ ] Create `app/models/checklist_item.py`: `ChecklistItem` model
- [ ] Export all models from `app/models/__init__.py`
- [ ] Run `alembic init alembic` and configure `alembic.ini` and `alembic/env.py` for async engine
- [ ] Generate initial migration: `alembic revision --autogenerate -m "initial"`
- [ ] Apply migration: `alembic upgrade head`
- [ ] Verify all tables created correctly in PostgreSQL

---

## Sub-Task 3 — Single-Team Authentication

**Status:** `[ ] pending`

- [ ] Create `app/core/security.py`: `verify_password()`, `create_access_token()`, `decode_access_token()`
- [ ] Create `app/schemas/auth.py`: `LoginRequest`, `TokenResponse`
- [ ] Create `app/api/auth.py`: `POST /auth/login` router
- [ ] Register auth router in `main.py`
- [ ] Create `app/core/deps.py`: `get_current_session` FastAPI dependency (validates JWT Bearer token)
- [ ] Write unit tests in `backend/tests/test_auth.py`:
  - Valid credentials → 200 + token
  - Invalid credentials → 401
  - Missing/invalid token on protected endpoint → 401
  - Expired token → 401

---

## Sub-Task 4 — Document Upload & File Storage Service

**Status:** `[ ] pending`

- [ ] Create `app/services/storage.py`: `StorageService` with `save_file()` and `delete_file()`
- [ ] Create `app/schemas/document.py`: `DocumentOut`, `DocumentUploadResponse`, `ShipmentOut`, `ShipmentCreate`
- [ ] Create `app/api/shipments.py` router:
  - [ ] `POST /shipments` — create session
  - [ ] `GET /shipments` — list sessions
  - [ ] `GET /shipments/{id}` — session detail
  - [ ] `POST /shipments/{id}/documents` — upload document
  - [ ] `GET /shipments/{id}/documents` — list documents
- [ ] Register shipments router in `main.py`
- [ ] Add MIME type validation (check file content headers, not just extension)
- [ ] Add 20 MB file size limit via FastAPI settings
- [ ] Write integration tests in `backend/tests/test_upload.py`:
  - Upload valid PDF → 202 + Document record created
  - Upload invalid MIME type → 400
  - Upload oversized file → 413

---

## Sub-Task 5 — OCR & Document Parsing Pipeline

**Status:** `[ ] pending`

- [ ] Define `ParsedDocument` dataclass in `app/utils/parsers.py`
- [ ] Implement `parse_pdf(path) -> ParsedDocument` using pdfplumber with OCR fallback
- [ ] Implement `parse_image(path) -> ParsedDocument` using Pillow + Tesseract
- [ ] Implement `parse_docx(path) -> ParsedDocument` using python-docx
- [ ] Implement `parse_xlsx(path) -> ParsedDocument` using openpyxl
- [ ] Implement `parse_document(path, mime_type) -> ParsedDocument` dispatcher
- [ ] Add image pre-processing before OCR: grayscale, deskew, contrast enhancement
- [ ] Add OCR language config from `OCR_LANG` env var
- [ ] Add low-yield PDF detection threshold (configurable, default 50 chars/page)
- [ ] Add sample fixture files to `docs/fixtures/` for testing
- [ ] Write unit tests in `backend/tests/test_parsers.py` for each parser using fixtures

---

## Sub-Task 6 — AI-Powered Structured Data Extraction

**Status:** `[ ] pending`

- [ ] Define canonical field schema and severity map in `app/core/fields.py`
- [ ] Create `app/services/llm.py`:
  - [ ] `LLMProvider` Protocol
  - [ ] `OpenAIProvider` implementation
  - [ ] `WatsonxProvider` implementation
  - [ ] `get_llm_provider()` factory (reads `LLM_PROVIDER` env var)
- [ ] Create `app/services/extraction.py`: `ExtractionService.extract(parsed_doc, doc_type)`
  - [ ] Build structured JSON extraction prompt per doc_type
  - [ ] Call LLM provider
  - [ ] Parse and validate JSON response
  - [ ] Return `list[ExtractedField]`
- [ ] Persist `ExtractedField` rows to DB
- [ ] Update `Document.extraction_status` to `done` or `failed`
- [ ] Write tests with mocked LLM in `backend/tests/test_extraction.py`

---

## Sub-Task 7 — Discrepancy Detection Engine

**Status:** `[ ] pending`

- [ ] Create `app/services/discrepancy.py`: `DiscrepancyEngine` class
- [ ] Implement `compare_fields(field_name, value_a, value_b) -> Discrepancy | None`
  - [ ] Numeric comparison with configurable tolerance (`NUMERIC_TOLERANCE` env var)
  - [ ] String normalisation (lowercase, strip whitespace)
  - [ ] Date normalisation (parse to date object before comparing)
  - [ ] Severity lookup from `app/core/fields.py`
- [ ] Implement `DiscrepancyEngine.run(shipment_id)`:
  - [ ] Load all documents and their extracted fields for the session
  - [ ] Identify document pairs sharing at least one canonical field
  - [ ] Call `compare_fields` for each shared field pair
  - [ ] Persist all `Discrepancy` records
- [ ] Implement `generate_checklist(shipment_id) -> list[ChecklistItem]`:
  - [ ] All 5 document types present
  - [ ] All documents extraction status `done`
  - [ ] No open `critical` discrepancies
  - [ ] Key fields consistent: `hs_code`, `port_of_loading`, `port_of_discharge`, `total_quantity`
- [ ] Persist `ChecklistItem` records
- [ ] Add `POST /shipments/{id}/analyse` endpoint (returns 202, enqueues background task)
- [ ] Write tests in `backend/tests/test_discrepancy.py`

---

## Sub-Task 8 — REST API — Reports & Dashboard Endpoints

**Status:** `[ ] pending`

- [ ] Add to `app/api/shipments.py`:
  - [ ] `GET /shipments/{id}/discrepancies` with optional severity/status filters
  - [ ] `PATCH /shipments/{id}/discrepancies/{disc_id}` — update status
  - [ ] `GET /shipments/{id}/checklist`
  - [ ] `GET /shipments/{id}/report/pdf` — stream PDF
- [ ] Create `app/services/report.py`: `generate_pdf_report(shipment_id, db) -> bytes`
- [ ] Create `app/templates/report.html`: Jinja2 template with:
  - [ ] Shipment summary header
  - [ ] Documents table
  - [ ] Discrepancies table grouped by severity with colour coding
  - [ ] Checklist pass/fail section
  - [ ] Generation timestamp and readiness score
- [ ] Add `GET /dashboard` endpoint in a new `app/api/dashboard.py` router
- [ ] Register dashboard router in `main.py`
- [ ] Write endpoint tests in `backend/tests/test_reports.py`

---

## Sub-Task 9 — Background Task Processing

**Status:** `[ ] pending`

- [ ] Create `app/tasks/process_document.py`:
  - [ ] `process_document_task(document_id, db)`: parse → extract → update status
  - [ ] Auto-trigger `DiscrepancyEngine.run()` when all session documents are `done`
- [ ] Refactor `POST /shipments/{id}/documents` to enqueue `process_document_task` via FastAPI `BackgroundTasks`
- [ ] Refactor `POST /shipments/{id}/analyse` to run as background task
- [ ] Add optional Celery wiring in `app/core/worker.py` (switchable via `TASK_BACKEND` env var)
- [ ] Write tests in `backend/tests/test_tasks.py`:
  - Upload returns 202 immediately
  - Document status transitions: pending → processing → done
  - Failed extraction sets status to `failed`

---

## Sub-Task 10 — Frontend: App Shell, Auth & Routing

**Status:** `[ ] pending`

- [ ] Configure Axios instance in `src/lib/api.ts`:
  - [ ] `baseURL` from `VITE_API_BASE_URL`
  - [ ] Request interceptor: attach JWT from localStorage
  - [ ] Response interceptor: redirect to `/login` on 401
- [ ] Create `src/context/AuthContext.tsx`: `isLoggedIn`, `login()`, `logout()`
- [ ] Create `src/pages/Login.tsx` with React Hook Form
- [ ] Create `src/components/ProtectedRoute.tsx`
- [ ] Set up React Router routes: `/login`, `/dashboard`, `/shipments`, `/shipments/:id`, `/shipments/:id/report`
- [ ] Create `src/components/AppLayout.tsx` with sidebar navigation
- [ ] Configure React Query `QueryClient` in `src/main.tsx`
- [ ] Verify login flow end-to-end against backend

---

## Sub-Task 11 — Frontend: Shipment Sessions & Document Upload UI

**Status:** `[ ] pending`

- [ ] Create `src/pages/Shipments.tsx`: sessions list with status badges and "New Shipment" button
- [ ] Create `src/components/CreateShipmentModal.tsx`
- [ ] Create `src/pages/ShipmentDetail.tsx`: document list with extraction status chips
- [ ] Add "Run Analysis" button on ShipmentDetail that calls `POST /shipments/{id}/analyse`
- [ ] Create `src/components/DocumentUpload.tsx`:
  - [ ] Drag-and-drop file input
  - [ ] Document type selector dropdown
  - [ ] Upload button with progress indicator
- [ ] Implement React Query polling (`refetchInterval: 3000`) until all documents are `done`/`failed`
- [ ] Add react-hot-toast notifications for upload success and failure

---

## Sub-Task 12 — Frontend: Discrepancy Review & Checklist UI

**Status:** `[ ] pending`

- [ ] Create `src/pages/DiscrepancyReview.tsx`: discrepancies grouped by severity
- [ ] Create `src/components/DiscrepancyCard.tsx`:
  - [ ] Field name, document A value, document B value
  - [ ] Document type labels for each side
  - [ ] Severity badge (red/amber/blue)
  - [ ] Status dropdown (open → acknowledged → resolved)
- [ ] Implement optimistic update via React Query mutation for status change
- [ ] Create `src/components/ChecklistPanel.tsx`: pass/fail cards with notes
- [ ] Add overall readiness score as a percentage progress bar

---

## Sub-Task 13 — Frontend: Dashboard & PDF Report Download

**Status:** `[ ] pending`

- [ ] Create `src/pages/Dashboard.tsx`:
  - [ ] Stat cards: total sessions, open critical/warning/info discrepancies
  - [ ] Recent sessions table with status badges and links
  - [ ] Donut chart (Recharts) for pass/fail ratio
- [ ] Add "Download Report" button on `ShipmentDetail.tsx`:
  - [ ] Call `GET /shipments/{id}/report/pdf`
  - [ ] Trigger browser blob download
- [ ] Handle loading and error states for all dashboard queries

---

## Sub-Task 14 — End-to-End Testing, Containerisation & Documentation

**Status:** `[ ] pending`

- [ ] Create fixture documents in `docs/fixtures/`:
  - [ ] `invoice.pdf` (1,200 cartons)
  - [ ] `packing_list.pdf` (1,180 cartons — intentional discrepancy)
  - [ ] `shipping_bill.pdf`
- [ ] Write E2E test in `backend/tests/test_e2e.py`:
  - [ ] Login → create session → upload 3 docs → analyse → discrepancy detected (carton count) → PDF downloaded
- [ ] Write `backend/Dockerfile`:
  - [ ] Python slim base
  - [ ] Install system deps: `tesseract-ocr`, `poppler-utils`, `libcairo2`, `fonts-liberation`
- [ ] Write `frontend/Dockerfile`: Node build stage + nginx serve stage
- [ ] Write `docker-compose.prod.yml`: backend + frontend + PostgreSQL
- [ ] Add nginx `proxy_pass /api` config in frontend Docker image
- [ ] Update `README.md` with Docker deployment section
- [ ] Run full test suite (`pytest backend/tests/`) — all tests green
- [ ] Fix any failures found during E2E run
