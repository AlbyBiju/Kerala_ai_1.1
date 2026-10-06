# ExportGuard — Export Document Verification System

> **"Verify Before You Ship"** — Automated cross-document verification, discrepancy analysis, and customs readiness certification for maritime and air freight exports.

---

## 1. System Overview

Export shipments require consistency across legally binding trade documents:
- **Commercial Invoice**
- **Packing List**
- **Shipping Bill** (Bill of Lading)
- **Purchase Order**
- **Quality Certificate** (Phytosanitary/Lab Analysis)

ExportGuard ingests files in PDF, image (PNG/JPEG/TIFF), Word, and Excel formats, parses text via digital extraction and OCR (Tesseract), uses AI to extract 24 canonical fields into structured JSON, cross-references values across document pairs, flags discrepancies with severity tiers (`critical`, `warning`, `info`), and evaluates an export readiness checklist.

---

## 2. Project Architecture

- **Backend**: Python 3.11+, FastAPI REST API, SQLAlchemy 2.0 Async (aiosqlite & asyncpg PostgreSQL), Pydantic v2 schemas.
- **Frontend**: React 19, TypeScript, Vite, TailwindCSS v4, TanStack React Query, React Router v7, React Hook Form, Recharts.
- **AI Extraction**: OpenAI & IBM watsonx providers with heuristic/regex offline fallback engine.
- **Reporting**: Jinja2 HTML templates and WeasyPrint PDF reports.

---

## 3. Quickstart Guide

### A. Backend Setup

```bash
cd backend

# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (pre-configured for local development)
cp .env.example .env

# 3. Run automated test suite (all 9 unit & e2e tests)
python -m pytest tests/ -v

# 4. Start the FastAPI server
python -m uvicorn main:app --reload --port 8000
```

The API documentation will be available at: `http://localhost:8000/docs`

Shared Team Credentials:
- **Username**: `team`
- **Password**: `secret`

### B. Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Build for production or start development server
npm run build
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## 4. Running with Docker Compose

```bash
docker-compose up -d
```

Services:
- **PostgreSQL**: `localhost:5432`
- **FastAPI Backend**: `localhost:8000`
- **React Frontend**: `localhost:5173`

---

## 5. Canonical Fields & Severities

ExportGuard cross-verifies 24 canonical fields. Mismatches in legal and customs fields (`total_quantity`, `total_weight_kg`, `total_value_usd`, `number_of_cartons`, `hs_code`) are classified as **Critical** blockers. Descriptive fields (`exporter_name`, `importer_name`, `product_description`, `port_of_loading`, `port_of_discharge`, `shipment_date`) are flagged as **Warning**.