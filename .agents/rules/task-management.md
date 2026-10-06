# Task Management & Development Workflow Rules

## 1. Authoritative Task Tracking

- The project source of truth is [TASKS.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/TASKS.md).
- Sub-tasks are sequentially numbered from Sub-Task 1 to Sub-Task 14:
  - Sub-Task 1: Project Scaffolding & Repository Structure
  - Sub-Task 2: Database Models & Migrations
  - Sub-Task 3: Single-Team Authentication
  - Sub-Task 4: Document Upload & File Storage Service
  - Sub-Task 5: OCR & Document Parsing Pipeline
  - Sub-Task 6: AI-Powered Structured Data Extraction
  - Sub-Task 7: Discrepancy Detection Engine
  - Sub-Task 8: REST API — Reports & Dashboard Endpoints
  - Sub-Task 9: Background Task Processing
  - Sub-Task 10: Frontend App Shell, Auth & Routing
  - Sub-Task 11: Frontend Shipment Sessions & Upload UI
  - Sub-Task 12: Frontend Discrepancy Review & Checklist UI
  - Sub-Task 13: Frontend Dashboard & PDF Report Download
  - Sub-Task 14: E2E Testing, Containerisation & Documentation

## 2. Execution Discipline

When working on a sub-task:
1. **Prerequisite Check**: Confirm that all earlier sub-tasks are marked `[x] complete`.
2. **Implementation**: Implement the code changes required in the sub-task.
3. **Automated Testing**: Run unit/integration tests covering the newly added functionality:
   - Backend: `pytest backend/tests/ -v`
   - Frontend: `npm test` or type-check `npm run build`
4. **Code Quality**:
   - Format: `black app/ tests/`
   - Lint: `ruff check app/ tests/`
5. **Documentation & Changelog**:
   - Mark completed items `[x]` in [TASKS.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/TASKS.md).
   - Add completed features under `## [Unreleased]` in [CHANGELOG.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/CHANGELOG.md).
   - If any new environment variables or endpoints were created, document them in [REFERENCE.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/REFERENCE.md).
