# Contributing to ResumeShield

Thank you for your interest in contributing. This document explains how to get the project running locally, the code standards we enforce, and the process for submitting changes.

---

## Local Dev Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional, for the full stack)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m spacy download en_core_web_sm
cp .env.example .env              # fill in your keys
uvicorn app.main:app --reload
```

API is available at http://localhost:8000. OpenAPI docs at http://localhost:8000/docs.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App is available at http://localhost:5173.

### Full stack with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## Code Standards

### Python

We use **black** for formatting and **ruff** for linting. Configuration lives in `backend/pyproject.toml`.

```bash
# Format
black backend/

# Lint (auto-fix)
ruff check backend/ --fix

# Type check
mypy backend/app
```

Line length: 100. Target Python version: 3.11.

### TypeScript / React

We use **ESLint** (flat config) and **Prettier**. Configuration lives in `frontend/eslint.config.js` and `frontend/.prettierrc`.

```bash
cd frontend
npm run lint            # ESLint check
npx prettier --check .  # Prettier check
npx prettier --write .  # Auto-format
```

Rules enforced:
- `react-hooks/rules-of-hooks` — error
- `react-hooks/exhaustive-deps` — warning
- `@typescript-eslint/no-explicit-any` — warning

---

## Testing

### Backend

```bash
cd backend
pytest -v                                   # all tests
pytest --cov=app --cov-report=html          # with HTML coverage
pytest --cov=app --cov-fail-under=60        # CI threshold
```

Tests live in `backend/tests/`. Fixtures are in `tests/conftest.py`. Use `pytest-asyncio` for async endpoint tests.

### Frontend

```bash
cd frontend
npm run test             # vitest run (single pass)
npm run test:coverage    # with v8 coverage report
```

Tests live in `frontend/src/__tests__/`. Use `@testing-library/react` for component tests.

---

## PR Process

1. Fork the repo and create a branch from `main`:
   ```
   git checkout -b feat/my-feature
   ```
2. Make your changes, adding tests for new behaviour.
3. Ensure all tests pass and linting is clean before opening a PR.
4. Open a pull request against `main` with a clear description of what changed and why.
5. A maintainer will review within a few days. Address feedback, and the PR will be merged once approved.

Please keep PRs focused — one feature or fix per PR.

---

## Commit Message Format

We follow a simplified [Conventional Commits](https://www.conventionalcommits.org/) style:

```
<type>: <short summary>

[optional body]
```

Types:
- `feat` — new feature
- `fix` — bug fix
- `chore` — tooling, deps, config
- `docs` — documentation only
- `test` — adding or updating tests
- `refactor` — code change that neither fixes a bug nor adds a feature
- `perf` — performance improvement

Examples:
```
feat: add grammar scoring to ATS engine
fix: handle empty resume text in section parser
chore: upgrade FastAPI to 0.115
docs: add architecture diagram to README
```

---

## Reporting Issues

Open a GitHub Issue with:
- A clear title
- Steps to reproduce (if a bug)
- Expected vs. actual behaviour
- Relevant logs or screenshots

