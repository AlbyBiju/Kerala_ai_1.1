# Changelog — Export Document Verification System

All notable changes to this project are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- Project scaffolding and repository structure
- Database models and Alembic migrations
- Single-team JWT authentication
- Document upload and file storage service
- OCR and document parsing pipeline (PDF, image, DOCX, XLSX, scanned)
- AI-powered structured data extraction (OpenAI / IBM watsonx)
- Discrepancy detection engine with severity classification
- Export readiness checklist generation
- REST API for reports, discrepancies, and dashboard
- Background task processing (FastAPI BackgroundTasks + optional Celery)
- React frontend: login, shipment sessions, document upload UI
- Discrepancy review and checklist UI
- Dashboard with statistics and PDF report download
- Docker containerisation (backend + frontend + PostgreSQL)
- End-to-end test suite

---

## [0.1.0] — Initial Release *(pending)*

### Added
- First working build of the Export Document Verification System
- Support for Commercial Invoice, Packing List, Shipping Bill, Purchase Order,
  and Quality Certificate document types
- PDF, PNG, JPEG, TIFF, DOCX, XLSX, and scanned document upload via OCR
- AI extraction of 24 canonical fields across document types
- Automatic discrepancy detection with critical/warning/info severity levels
- Export readiness checklist (5 checks per session)
- PDF summary report generation
- Summary dashboard with aggregate statistics
- Single-team shared JWT authentication
- Persistent shipment session history
- Docker Compose setup for local development

---

*Entries will be added here as sub-tasks are completed during implementation.*
