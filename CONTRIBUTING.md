# Contributing — Export Document Verification System

## Prerequisites

Ensure the following are installed before working on this project:

| Tool | Version | Notes |
|---|---|---|
| Python | 3.11+ | Backend |
| Node.js | 20+ | Frontend |
| PostgreSQL | 15+ | Via Docker recommended |
| Docker + Docker Compose | Latest | For local DB and prod builds |
| Tesseract OCR | 5+ | System binary for OCR parsing |
| Poppler | Latest | System binary for pdf2image |
| Cairo | Latest | System library for WeasyPrint |

### Install system dependencies

**macOS:**
```bash
brew install tesseract poppler cairo
```

**Ubuntu / Debian:**
```bash
sudo apt-get install -y tesseract-ocr poppler-utils libcairo2 fonts-liberation
```

**Windows:**
- Tesseract: download from https://github.com/UB-Mannheim/tesseract/wiki
- Poppler: download from https://github.com/oschwartz10612/poppler-windows/releases
- Add both to `PATH`

---

## Local Development Setup

### 1. Clone and enter the project
```bash
git clone <repo-url>
cd export-doc-verification
```

### 2. Start the database
```bash
docker-compose up -d
```

### 3. Backend setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — fill in TEAM_USERNAME, TEAM_PASSWORD, JWT_SECRET, OPENAI_API_KEY
alembic upgrade head
uvicorn main:app --reload --port 8000
```

### 4. Frontend setup
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

To run a specific test file:
```bash
pytest tests/test_discrepancy.py -v
```

To run with coverage:
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Code Style

### Backend (Python)
- Formatter: **black** (`black app/ tests/`)
- Linter: **ruff** (`ruff check app/ tests/`)
- Type checking: **mypy** (`mypy app/`)
- All new modules must have type hints on public functions
- Docstrings required for all service classes and public methods

### Frontend (TypeScript / React)
- Formatter: **Prettier** (`npm run format`)
- Linter: **ESLint** (`npm run lint`)
- All components must be typed with TypeScript interfaces (no `any`)
- Use React Query for all server state — no `useEffect` for data fetching

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, production-ready code |
| `dev` | Integration branch for completed sub-tasks |
| `feat/<name>` | Feature branches for individual sub-tasks |
| `fix/<name>` | Bug fix branches |

**Workflow:**
1. Branch from `dev`: `git checkout -b feat/subtask-5-ocr-parsing`
2. Implement the sub-task
3. Run tests and linting locally
4. Open a pull request into `dev`
5. After review and merge, update task status in `TASKS.md`
6. Merge `dev` → `main` for releases

---

## Pull Request Checklist

Before opening a PR, confirm:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] No new linting errors (`ruff check app/`)
- [ ] Code is formatted (`black app/`)
- [ ] New env vars are added to `.env.example` and documented in `REFERENCE.md`
- [ ] Task status updated in `TASKS.md`
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] New API endpoints documented in `REFERENCE.md`

---

## Project Structure

See `ARCHITECTURE.md` for the full directory layout and data flow diagrams.

---

## Adding a New Document Type

1. Add a new value to the `doc_type` enum in `app/models/document.py`
2. Add the corresponding field list to `app/core/fields.py`
3. Add an extraction prompt branch in `app/services/extraction.py`
4. Update the checklist logic in `app/services/discrepancy.py` if needed
5. Generate and apply an Alembic migration
6. Update `REFERENCE.md` with the new document type and its fields
7. Add a fixture file under `docs/fixtures/` for testing

---

## Adding a New LLM Provider

1. Implement the `LLMProvider` protocol in `app/services/llm.py`
2. Add provider selection logic to `get_llm_provider()`
3. Add required env vars to `backend/.env.example` and `REFERENCE.md`
4. Write tests with a mocked provider in `backend/tests/test_extraction.py`

---

## Reporting Issues

Open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behaviour
- Environment details (OS, Python version, Docker version)
- Relevant log output
