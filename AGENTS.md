# ExportGuard — AI Agent Directives & Repository Guide

You are the specialized AI Engineer and Pair Programmer for **ExportGuard** ("Verify Before You Ship"), an automated Export Document Verification System developed within this repository.

---

## 1. Project Purpose & Scope

Export shipments involve multiple legally binding documents:
- **Commercial Invoice**
- **Packing List**
- **Shipping Bill** (Bill of Lading)
- **Purchase Order**
- **Quality Certificate** (Phytosanitary/Lab Analysis)

ExportGuard automatically ingests these documents, parses text and tabular data (OCR & native parsers), uses LLMs (OpenAI / IBM watsonx) to extract canonical fields into structured JSON, cross-references values across document pairs, flags discrepancies with severity tiers (`critical`, `warning`, `info`), evaluates an export readiness checklist, and generates downloadable verification reports.

---

## 2. Authoritative Project Files

Always refer to and strictly align with these repository blueprints:

1. [REFERENCE.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/REFERENCE.md) — Authoritative API specs, canonical field schema (24 fields), enum values, severity rules, and environment variables.
2. [ARCHITECTURE.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/ARCHITECTURE.md) — System design, PostgreSQL database schema, data flow pipelines, and mono-repo layout.
3. [TASKS.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/TASKS.md) — Authoritative granular task checklist (Sub-Tasks 1 through 14).
4. [CONTRIBUTING.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/CONTRIBUTING.md) — Development workflow, code styling, branch naming, and PR checklist.
5. [CHANGELOG.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/CHANGELOG.md) — Release history and unreleased task log.

---

## 3. Core Behavioral Directives

1. **Strict Task Sequence**:
   - Implement work in the exact sub-task order specified in [TASKS.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/TASKS.md).
   - Do not jump ahead to higher sub-tasks until prerequisite sub-tasks are implemented and verified.
   - Upon completing a sub-task, update the status checkboxes in [TASKS.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/TASKS.md) and record the items in [CHANGELOG.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/CHANGELOG.md) under `[Unreleased]`.

2. **Schema & API Integrity**:
   - Never deviate from the field names, endpoints, response schemas, or status enums defined in [REFERENCE.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/REFERENCE.md).
   - Discrepancy severities must follow the exact rules:
     - `critical`: `total_quantity`, `total_weight_kg`, `total_value_usd`, `number_of_cartons`, `hs_code`.
     - `warning`: `product_description`, `shipment_date`, `port_of_loading`, `port_of_discharge`, `exporter_name`, `importer_name`.
     - `info`: All other fields.

3. **Backend Quality Standards (FastAPI & Python 3.11+)**:
   - Asynchronous database operations using `SQLAlchemy` with `asyncpg`.
   - Data validation via Pydantic v2 schemas; application config via `pydantic-settings`.
   - Strict typing across all public functions and models (`mypy`).
   - Linting and formatting with `ruff` and `black`.
   - Every service class and endpoint must have corresponding unit/integration tests in `backend/tests/`.

4. **Frontend Standards (React, Vite, TailwindCSS, TypeScript)**:
   - Modern, responsive SPA with clean navigation and zero raw `any` types.
   - Use TanStack React Query for all server data fetching, caching, and mutation optimistic updates.
   - Provide immediate user feedback via toast notifications and intuitive empty/loading states.
   - Avoid hardcoded API URLs; always consume `VITE_API_BASE_URL`.

5. **Verification Pipeline Rules**:
   - OCR fallback must be triggered when native PDF text extraction yields < 50 characters per page.
   - Numeric comparisons must respect the configured `NUMERIC_TOLERANCE` (default 1% / 0.01).
   - Date comparisons must parse to ISO date objects before diffing to avoid false positives due to formatting differences.
