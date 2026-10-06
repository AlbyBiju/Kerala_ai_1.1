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

**Status:** `[x] complete`

- [x] Create root directory layout: `/backend`, `/frontend`, `/docs`, `/scripts`
- [x] Scaffold FastAPI project inside `/backend` with `main.py` and `app/` package
- [x] Create `app/` sub-packages: `api/`, `core/`, `models/`, `schemas/`, `services/`, `utils/`, `tasks/`, `templates/`
- [x] Add `backend/requirements.txt` with all dependencies
- [x] Scaffold React + Vite + TailwindCSS project inside `/frontend`
- [x] Install frontend dependencies: React Router, React Query, Axios, React Hook Form, react-hot-toast, Recharts
- [x] Add `docker-compose.yml` for PostgreSQL + pgAdmin (local dev)
- [x] Add `backend/.env.example` with all backend env vars
- [x] Add `frontend/.env.example` with `VITE_API_BASE_URL`
- [x] Write root `README.md` with local setup steps and system dependency notes

---

## Sub-Task 2 — Database Models & Migrations

**Status:** `[x] complete`

- [x] Configure SQLAlchemy async engine and session factory in `app/core/database.py`
- [x] Create `app/core/config.py` using pydantic-settings to load env vars
- [x] Create `app/models/shipment.py`: `ShipmentSession` model
- [x] Create `app/models/document.py`: `Document` model
- [x] Create `app/models/extracted_field.py`: `ExtractedField` model
- [x] Create `app/models/discrepancy.py`: `Discrepancy` model
- [x] Create `app/models/checklist_item.py`: `ChecklistItem` model
- [x] Export all models from `app/models/__init__.py`
- [x] Configure SQLite async engine and PostgreSQL asyncpg support with auto-initialisation
- [x] Verify all tables created correctly in database engine

---

## Sub-Task 3 — Single-Team Authentication

**Status:** `[x] complete`

- [x] Create `app/core/security.py`: `verify_password()`, `create_access_token()`, `decode_access_token()`
- [x] Create `app/schemas/auth.py`: `LoginRequest`, `TokenResponse`
- [x] Create `app/api/auth.py`: `POST /auth/login` router
- [x] Register auth router in `main.py`
- [x] Create `app/core/deps.py`: `get_current_session` FastAPI dependency (validates JWT Bearer token)
- [x] Write unit tests in `backend/tests/test_auth.py`:
  - Valid credentials → 200 + token
  - Invalid credentials → 401
  - Missing/invalid token on protected endpoint → 401
  - Expired token → 401

---

## Sub-Task 4 — Document Upload & File Storage Service

**Status:** `[x] complete`

- [x] Create `app/services/storage.py`: `StorageService` with `save_file()` and `delete_file()`
- [x] Create `app/schemas/document.py`: `DocumentOut`, `DocumentUploadResponse`, `ShipmentOut`, `ShipmentCreate`
- [x] Create `app/api/shipments.py` router:
  - [x] `POST /shipments` — create session
  - [x] `GET /shipments` — list sessions
  - [x] `GET /shipments/{id}` — session detail
  - [x] `POST /shipments/{id}/documents` — upload document
  - [x] `GET /shipments/{id}/documents` — list documents
- [x] Register shipments router in `main.py`
- [x] Add MIME type validation (check file content headers and extensions)
- [x] Add 20 MB file size limit via FastAPI settings
- [x] Validate file upload in automated tests

---

## Sub-Task 5 — OCR & Document Parsing Pipeline

**Status:** `[x] complete`

- [x] Define `ParsedDocument` dataclass in `app/utils/parsers.py`
- [x] Implement `parse_pdf(path) -> ParsedDocument` using PyMuPDF / pdfplumber with OCR fallback
- [x] Implement `parse_image(path) -> ParsedDocument` using Pillow + Tesseract
- [x] Implement `parse_docx(path) -> ParsedDocument` using python-docx
- [x] Implement `parse_xlsx(path) -> ParsedDocument` using openpyxl
- [x] Implement `parse_document(path, mime_type) -> ParsedDocument` dispatcher
- [x] Add image pre-processing before OCR: grayscale, deskew, contrast enhancement
- [x] Add OCR language config from `OCR_LANG` env var
- [x] Add low-yield PDF detection threshold (< 50 chars/page)

---

## Sub-Task 6 — AI-Powered Structured Data Extraction

**Status:** `[x] complete`

- [x] Define canonical field schema and severity map in `app/core/fields.py`
- [x] Create `app/services/llm.py`:
  - [x] `LLMProvider` Protocol
  - [x] `OpenAIProvider` implementation
  - [x] `WatsonxProvider` implementation
  - [x] `RuleBasedFallbackProvider` heuristic/regex implementation for offline resilience
  - [x] `get_llm_provider()` factory (reads `LLM_PROVIDER` env var)
- [x] Create `app/services/extraction.py`: `ExtractionService.extract_document(document_id, db)`
  - [x] Build structured JSON extraction prompt per doc_type
  - [x] Call LLM provider
  - [x] Parse and validate response
  - [x] Persist `ExtractedField` rows to DB
  - [x] Update `Document.extraction_status` to `done` or `failed`

---

## Sub-Task 7 — Discrepancy Detection Engine

**Status:** `[x] complete`

- [x] Create `app/services/discrepancy.py`: `DiscrepancyEngine` class
- [x] Implement `compare_values(field_name, value_a, value_b)`:
  - [x] Numeric comparison with configurable tolerance (`NUMERIC_TOLERANCE` env var)
  - [x] String normalisation (lowercase, strip whitespace)
  - [x] Date normalisation (parse to ISO date object before comparing)
  - [x] Severity lookup from `app/core/fields.py`
- [x] Implement `DiscrepancyEngine.run(shipment_id)`:
  - [x] Load all documents and their extracted fields for the session
  - [x] Identify document pairs sharing at least one canonical field
  - [x] Call `compare_values` for each shared field pair
  - [x] Persist all `Discrepancy` records
- [x] Implement `generate_checklist(shipment_id) -> list[ChecklistItem]`:
  - [x] All 5 document types present
  - [x] All documents extraction status `done`
  - [x] No open `critical` discrepancies
  - [x] Legal / customs fields consistent: `hs_code`, `port_of_loading`, `port_of_discharge`
  - [x] Cargo metrics consistent: `total_quantity`, `total_weight_kg`, `number_of_cartons`
- [x] Persist `ChecklistItem` records
- [x] Add `POST /shipments/{id}/analyse` endpoint (returns 202, enqueues background task)
- [x] Write tests in `backend/tests/test_discrepancy.py`

---

## Sub-Task 8 — REST API — Reports & Dashboard Endpoints

**Status:** `[x] complete`

- [x] Add to `app/api/shipments.py`:
  - [x] `GET /shipments/{id}/discrepancies` with optional severity/status filters
  - [x] `PATCH /shipments/{id}/discrepancies/{disc_id}` — update status
  - [x] `GET /shipments/{id}/checklist`
  - [x] `GET /shipments/{id}/report/pdf` — stream PDF / report
- [x] Create `app/services/report.py`: `generate_report_content(shipment_id, db)`
- [x] Create `app/templates/report.html`: Jinja2 template
- [x] Add `GET /dashboard` endpoint in `app/api/dashboard.py` router
- [x] Register dashboard router in `main.py`

---

## Sub-Task 9 — Background Task Processing

**Status:** `[x] complete`

- [x] Create `app/tasks/process_document.py`:
  - [x] `process_document_task(document_id, shipment_id)`: parse → extract → trigger discrepancy check
  - [x] `run_analysis_task(shipment_id)`: trigger analysis task
- [x] Integrate with FastAPI `BackgroundTasks` on `POST /shipments/{id}/documents` and `POST /shipments/{id}/analyse`
- [x] Verified asynchronous transitions and status persistence

---

## Sub-Task 10 — Frontend: App Shell, Auth & Routing

**Status:** `[x] complete`

- [x] Configure Axios instance in `src/lib/api.ts` with token interceptor and 401 redirect
- [x] Configure `src/context/AuthContext.tsx`
- [x] Configure `src/pages/Login.tsx` with authentication form
- [x] Configure `src/components/ProtectedRoute.tsx`
- [x] Set up routes: `/login`, `/dashboard`, `/shipments`, `/shipments/:id`
- [x] Configure `src/components/AppLayout.tsx` with top/sidebar navigation
- [x] Configure React Query `QueryClient` in `src/main.tsx`

---

## Sub-Task 11 — Frontend: Shipment Sessions & Document Upload UI

**Status:** `[x] complete`

- [x] Configure `src/pages/Shipments.tsx` with status badges and "New Shipment" modal
- [x] Configure `src/components/CreateShipmentModal.tsx`
- [x] Configure `src/pages/ShipmentDetail.tsx` with document chips and "Run Analysis" trigger
- [x] Configure `src/components/DocumentUpload.tsx` with drag-and-drop and doc type selector
- [x] Real-time polling via React Query (`refetchInterval: 3000`)
- [x] Feedback notifications with `react-hot-toast`

---

## Sub-Task 12 — Frontend: Discrepancy Review & Checklist UI

**Status:** `[x] complete`

- [x] Configure `src/components/DiscrepancyReview.tsx` grouped by severity
- [x] Field comparisons with document values and severity badges (red/amber/blue)
- [x] Interactive status updater (open → acknowledged → resolved) with optimistic mutation
- [x] Configure `src/components/ChecklistPanel.tsx` with pass/fail evaluation cards
- [x] Overall readiness score gauge

---

## Sub-Task 13 — Frontend: Dashboard & PDF Report Download

**Status:** `[x] complete`

- [x] Configure `src/pages/Dashboard.tsx` with KPI cards (total sessions, open issues by severity)
- [x] Recent shipment sessions table
- [x] Donut chart visualization for verification pass rate
- [x] "Download Report" button streaming PDF/HTML report from backend
- [x] Loading skeleton and error state handling

---

## Sub-Task 14 — End-to-End Testing, Containerisation & Documentation

**Status:** `[x] complete`

- [x] Automated E2E verification test in `backend/tests/test_e2e.py` covering login, session creation, upload, discrepancy detection (1200 vs 1180 cartons), checklist, dashboard, and report download
- [x] `docker-compose.yml` for multi-container orchestration (backend, frontend, postgres)
- [x] Comprehensive root `README.md`
- [x] Full test suite green (9 passed in pytest)
- [x] Frontend production build compiled without errors (`tsc -b && vite build`)
