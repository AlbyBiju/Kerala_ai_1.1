# Changelog — Export Document Verification System

All notable changes to this project are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2026-10-07

### Added
- **Core Architecture & Scaffolding**: FastAPI async application layout, SQLAlchemy 2.0 async engine (`aiosqlite` & `asyncpg`), and Pydantic v2 schemas.
- **Data Models**: Persisted models for `ShipmentSession`, `Document`, `ExtractedField`, `Discrepancy`, and `ChecklistItem`.
- **Authentication**: JWT token-based authentication with bcrypt password verification on `POST /auth/login` and Bearer dependency injection.
- **Storage Service**: Ingestion and secure file persistence supporting up to 20 MB with MIME/extension validation on `POST /shipments/{id}/documents`.
- **Parsing Pipeline**: Multi-format document parser dispatching PDF (PyMuPDF with OCR fallback threshold < 50 chars/page), images (Pillow + Tesseract), Word (`.docx`), and Excel (`.xlsx`).
- **AI Extraction Service**: Structured extraction against 24 canonical fields supporting OpenAI, IBM watsonx, and intelligent rule-based offline fallback.
- **Discrepancy Engine**: Pairwise document field comparator with configurable numeric tolerance (`0.01`), date normalization, string sanitization, and severity classification (`critical`, `warning`, `info`).
- **Export Readiness Checklist**: 5-point verification checklist evaluating document completeness, extraction success, zero critical discrepancies, legal consistency, and quantity reconciliation.
- **REST API Suite**: Complete shipment CRUD, discrepancy filtering and patching, checklist evaluation, and dashboard KPI statistics (`GET /dashboard`).
- **Report Generation**: Jinja2 templating with WeasyPrint / HTML streaming on `GET /shipments/{id}/report/pdf`.
- **React Frontend SPA**: Responsive SPA with login, dashboard, shipment management, drag-and-drop upload, discrepancy review cards with status switching, and checklist panels.
- **Testing & Containerisation**: 9 automated unit and end-to-end integration tests (`pytest`) and Docker Compose configuration.

### Fixed
- **PDF reports were actually HTML**: WeasyPrint is unavailable on Windows, so `GET /shipments/{id}/report/pdf` silently returned HTML bytes named `.pdf`. Replaced with PyMuPDF Story rendering (cross-platform, no system deps; WeasyPrint kept as fallback) — verified `%PDF-1.7` output with 3 pages of content
- Backend test environment: project venv on Python 3.13 (Python 3.14 site-packages blocked by Application Control policy)
- `requirements.txt`: added `sqlalchemy[asyncio]` extra (greenlet) and `aiofiles`
- `parse_pdf()` no longer hard-fails on corrupt/mislabeled PDFs — falls back to plain-text decode so extraction can proceed
- Storage service now validates uploaded file content by magic bytes, not just extension/MIME (rejects fake PDFs/images with 400)

### Added
- Real PDF fixtures (`docs/fixtures/invoice.pdf`, `packing_list.pdf`, `shipping_bill.pdf`) via `scripts/generate_fixtures.py` and `tests/conftest.py`
- Tests: upload content validation (202/400/413), parser dispatcher (PDF/XLSX/DOCX/corrupt fallback), extraction with mocked LLM — 18 passing
- Alembic async migrations wired to app models (`alembic revision --autogenerate`, `upgrade head`)
- Optional Celery task backend (`app/core/worker.py`, `TASK_BACKEND=celery`)
- Production deployment: `docker-compose.prod.yml` with healthchecks and secrets, frontend nginx `/api` proxy, root `.gitignore`
