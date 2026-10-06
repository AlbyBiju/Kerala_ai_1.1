---
name: exportguard-task-runner
description: >-
  Use this skill when implementing, testing, or updating any sub-task from TASKS.md in the ExportGuard / Kerala_ai project. Guides sequential task progression, test execution, linting, and changelog updates.
---

# ExportGuard Task Runner Skill

This skill provides the standardized workflow for executing and validating sub-tasks from [TASKS.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/TASKS.md).

---

## Workflow Steps

### Step 1: Identify Target Sub-Task
1. Read [TASKS.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/TASKS.md) to locate the first uncompleted sub-task (`[ ] pending` or `[-] in progress`).
2. Verify that all preceding sub-tasks are marked `[x] complete`. Do not proceed if dependencies are missing.
3. Review corresponding design specifications in [ARCHITECTURE.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/ARCHITECTURE.md) and [REFERENCE.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/REFERENCE.md).

### Step 2: Implementation
1. Ensure you are working inside the `Kerala_ai/` repository directory.
2. Implement backend code under `backend/` or frontend code under `frontend/`.
3. Follow the rules defined in `.agents/rules/code-standards.md`.
4. Ensure all new models, schemas, and endpoints conform exactly to [REFERENCE.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/REFERENCE.md).

### Step 3: Verification & Automated Tests
1. For backend sub-tasks:
   ```bash
   cd backend
   pytest tests/ -v
   black --check app/ tests/
   ruff check app/ tests/
   ```
2. For frontend sub-tasks:
   ```bash
   cd frontend
   npm run lint
   npm run build
   ```
3. Fix any regressions or failures before proceeding.

### Step 4: Status Updates
1. Mark the completed sub-task check items with `[x]` in [TASKS.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/TASKS.md).
2. Update the sub-task header status from `[ ] pending` to `[x] complete`.
3. Update [CHANGELOG.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/CHANGELOG.md) under the `## [Unreleased]` section with a concise summary of changes.
4. If new environment variables were introduced, add them to `backend/.env.example` or `frontend/.env.example` and update [REFERENCE.md](file:///c:/Users/Abel%20Jose/Desktop/keralai/Kerala_ai/REFERENCE.md).
