# Reference — Export Document Verification System

## REST API Reference

### Base URL
```
http://localhost:8000
```
All endpoints (except `/auth/login`) require:
```
Authorization: Bearer <jwt_token>
```

---

### Authentication

#### `POST /auth/login`
Authenticate with shared team credentials and receive a JWT.

**Request body:**
```json
{
  "username": "team",
  "password": "secret"
}
```

**Response `200`:**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

**Response `401`:**
```json
{ "detail": "Invalid credentials" }
```

---

### Shipment Sessions

#### `POST /shipments`
Create a new shipment session.

**Request body:**
```json
{
  "name": "Shipment #INV-2024-001",
  "description": "Seafood export to Singapore"
}
```

**Response `201`:** `ShipmentSession` object

---

#### `GET /shipments`
List all shipment sessions, newest first.

**Response `200`:** Array of `ShipmentSession` objects

---

#### `GET /shipments/{id}`
Get details of a single shipment session.

**Response `200`:** `ShipmentSession` object with embedded document list

**Response `404`:** Session not found

---

#### `POST /shipments/{id}/documents`
Upload a document into a session. Accepts `multipart/form-data`.

**Form fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | Yes | Document file (PDF/PNG/JPEG/TIFF/DOCX/XLSX) |
| `doc_type` | string | Yes | One of the doc type enum values (see below) |

**Response `202`:**
```json
{
  "id": "<uuid>",
  "doc_type": "commercial_invoice",
  "original_filename": "invoice.pdf",
  "extraction_status": "pending"
}
```

**Errors:** `400` invalid MIME type · `413` file too large (>20 MB) · `404` session not found

---

#### `GET /shipments/{id}/documents`
List all documents for a session.

**Response `200`:** Array of `Document` objects

---

#### `POST /shipments/{id}/analyse`
Trigger discrepancy analysis for the session (runs as background task).

**Response `202`:**
```json
{ "detail": "Analysis started" }
```

---

#### `GET /shipments/{id}/discrepancies`
List all discrepancies found for the session.

**Query parameters:**

| Param | Type | Description |
|---|---|---|
| `severity` | string | Filter by `critical`, `warning`, or `info` |
| `status` | string | Filter by `open`, `acknowledged`, or `resolved` |

**Response `200`:** Array of `Discrepancy` objects

---

#### `PATCH /shipments/{id}/discrepancies/{disc_id}`
Update the status of a discrepancy.

**Request body:**
```json
{ "status": "acknowledged" }
```

**Response `200`:** Updated `Discrepancy` object

---

#### `GET /shipments/{id}/checklist`
Get the export readiness checklist for the session.

**Response `200`:** Array of `ChecklistItem` objects

---

#### `GET /shipments/{id}/report/pdf`
Download the full discrepancy report as a PDF.

**Response `200`:** `application/pdf` binary stream with
`Content-Disposition: attachment; filename="report-{id}.pdf"`

---

### Dashboard

#### `GET /dashboard`
Get aggregate statistics for the dashboard.

**Response `200`:**
```json
{
  "total_sessions": 42,
  "open_discrepancies": {
    "critical": 3,
    "warning": 7,
    "info": 12
  },
  "overall_pass_rate": 0.74,
  "recent_sessions": [
    {
      "id": "<uuid>",
      "name": "Shipment #INV-2024-001",
      "status": "reviewed",
      "created_at": "2024-01-15T09:30:00Z"
    }
  ]
}
```

---

## Response Schemas

### `ShipmentSession`
```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "status": "draft | processing | reviewed | closed",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

### `Document`
```json
{
  "id": "uuid",
  "shipment_id": "uuid",
  "doc_type": "commercial_invoice | packing_list | shipping_bill | purchase_order | quality_certificate",
  "original_filename": "string",
  "mime_type": "string",
  "extraction_status": "pending | processing | done | failed",
  "created_at": "ISO 8601 datetime"
}
```

### `ExtractedField`
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "field_name": "string",
  "field_value": "string",
  "confidence_score": 0.0,
  "page_number": 1
}
```

### `Discrepancy`
```json
{
  "id": "uuid",
  "shipment_id": "uuid",
  "field_name": "string",
  "document_a_id": "uuid",
  "document_a_value": "string",
  "document_b_id": "uuid",
  "document_b_value": "string",
  "severity": "critical | warning | info",
  "status": "open | acknowledged | resolved",
  "created_at": "ISO 8601 datetime"
}
```

### `ChecklistItem`
```json
{
  "id": "uuid",
  "shipment_id": "uuid",
  "label": "string",
  "is_passed": true,
  "notes": "string | null"
}
```

---

## Canonical Field Schema

These are the fields the AI extraction service attempts to extract per document type.
Fields marked ✓ are extracted and compared across documents during analysis.

| Field | Invoice | Packing List | Shipping Bill | PO | Quality Cert |
|---|---|---|---|---|---|
| `exporter_name` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `importer_name` | ✓ | ✓ | ✓ | ✓ | |
| `shipment_date` | ✓ | ✓ | ✓ | ✓ | |
| `total_quantity` | ✓ | ✓ | ✓ | ✓ | |
| `total_weight_kg` | ✓ | ✓ | ✓ | | |
| `total_value_usd` | ✓ | | | ✓ | |
| `currency` | ✓ | | | ✓ | |
| `hs_code` | ✓ | ✓ | ✓ | ✓ | |
| `product_description` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `port_of_loading` | ✓ | | ✓ | | |
| `port_of_discharge` | ✓ | | ✓ | | |
| `invoice_number` | ✓ | | | | |
| `payment_terms` | ✓ | | | | |
| `number_of_cartons` | | ✓ | | | |
| `gross_weight_kg` | | ✓ | | | |
| `net_weight_kg` | | ✓ | | | |
| `shipping_bill_number` | | | ✓ | | |
| `vessel_name` | | | ✓ | | |
| `voyage_number` | | | ✓ | | |
| `po_number` | | | | ✓ | |
| `buyer_ref` | | | | ✓ | |
| `certificate_number` | | | | | ✓ |
| `lab_name` | | | | | ✓ |
| `test_date` | | | | | ✓ |

---

## Document Type Enum Values

| Value | Description |
|---|---|
| `commercial_invoice` | Commercial Invoice |
| `packing_list` | Packing List |
| `shipping_bill` | Shipping Bill / Bill of Lading |
| `purchase_order` | Purchase Order |
| `quality_certificate` | Quality / Phytosanitary Certificate |

---

## Severity Rules

| Severity | Fields | Description |
|---|---|---|
| `critical` | `total_quantity`, `total_weight_kg`, `total_value_usd`, `number_of_cartons`, `hs_code` | Numeric or legal fields — mismatches likely cause customs holds |
| `warning` | `product_description`, `shipment_date`, `port_of_loading`, `port_of_discharge`, `exporter_name`, `importer_name` | Descriptive fields — mismatches may cause delays |
| `info` | All other fields | Minor differences unlikely to cause issues |

---

## Supported File Formats

| Format | MIME Type | Extraction Method |
|---|---|---|
| PDF (native text) | `application/pdf` | pdfplumber |
| PDF (scanned) | `application/pdf` | pdf2image + Tesseract OCR |
| PNG | `image/png` | Tesseract OCR |
| JPEG | `image/jpeg` | Tesseract OCR |
| TIFF | `image/tiff` | Tesseract OCR |
| Word | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | python-docx |
| Excel | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | openpyxl |

Maximum file size: **20 MB**

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | PostgreSQL async URL e.g. `postgresql+asyncpg://user:pass@localhost/dbname` |
| `JWT_SECRET` | Yes | — | Secret key for signing JWT tokens |
| `JWT_EXPIRE_MINUTES` | No | `480` | JWT validity duration in minutes |
| `TEAM_USERNAME` | Yes | — | Shared login username |
| `TEAM_PASSWORD` | Yes | — | Shared login password |
| `LLM_PROVIDER` | Yes | `openai` | `openai` or `watsonx` |
| `OPENAI_API_KEY` | Conditional | — | Required when `LLM_PROVIDER=openai` |
| `WATSONX_API_KEY` | Conditional | — | Required when `LLM_PROVIDER=watsonx` |
| `WATSONX_PROJECT_ID` | Conditional | — | Required when `LLM_PROVIDER=watsonx` |
| `WATSONX_URL` | Conditional | — | Required when `LLM_PROVIDER=watsonx` |
| `UPLOAD_DIR` | No | `./uploads` | Directory to store uploaded documents |
| `OCR_LANG` | No | `eng` | Tesseract language code |
| `NUMERIC_TOLERANCE` | No | `0.01` | Fractional tolerance for numeric field comparison (1%) |
| `TASK_BACKEND` | No | `local` | `local` (FastAPI BackgroundTasks) or `celery` |
| `CELERY_BROKER_URL` | Conditional | — | Required when `TASK_BACKEND=celery` |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | Yes | `http://localhost:8000` | Backend API base URL |
