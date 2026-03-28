# ResumeShield

**Pass the ATS. Fool the AI Detector. Land the Interview.**

![Python](https://img.shields.io/badge/Python-3.12-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![React](https://img.shields.io/badge/React-18-blue) ![TypeScript](https://img.shields.io/badge/TypeScript-5-blue) ![Docker](https://img.shields.io/badge/Docker-ready-blue)

**Live Demo: [https://resumeshield.vercel.app](https://resumeshield.vercel.app)**

---

## The Problem

- **75% of resumes** are rejected by ATS (Applicant Tracking Systems) before a human ever sees them
- **80% of AI-generated resumes** are flagged and rejected by hiring teams using AI detection tools
- No existing tool checks **both axes** simultaneously

## The Solution

ResumeShield is the first dual-axis resume scanner that scores your resume on **ATS keyword compatibility** AND **AI-generated text detection** simultaneously. Paste your resume and a job description, get actionable fixes in under 3 seconds.

## Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────┐
│   React + TS    │────▶│           FastAPI Backend             │
│   (Vite, TW)    │◀────│                                      │
└─────────────────┘     │  ┌──────────┐  ┌──────────────────┐  │
                        │  │   ATS    │  │  AI Detection    │  │
                        │  │  Engine  │  │    Engine (12     │  │
                        │  │(5 dims) │  │    signals)      │  │
                        │  └──────────┘  └──────────────────┘  │
                        │  ┌──────────┐  ┌──────────────────┐  │
                        │  │ Keyword  │  │  Section Parser  │  │
                        │  │Extractor │  │                  │  │
                        │  │ (spaCy)  │  │                  │  │
                        │  └──────────┘  └──────────────────┘  │
                        │  ┌──────────┐  ┌──────────────────┐  │
                        │  │   Fix    │  │   PDF Parser     │  │
                        │  │Generator │  │  (pdfplumber)    │  │
                        │  └──────────┘  └──────────────────┘  │
                        └──────────────────────────────────────┘
```

## Quick Start

### Docker (recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/scan` | Full resume scan (ATS + AI) |
| POST | `/api/v1/scan/file` | Scan uploaded PDF/DOCX |
| POST | `/api/v1/scan/quick` | Quick re-scan (scores only) |
| POST | `/api/v1/compare` | Before/after comparison |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/stats` | Global statistics |
| GET | `/api/v1/keywords/extract` | Extract keywords from JD |
| GET | `/api/v1/banned-phrases` | Get banned phrase list |

Full OpenAPI docs at `/docs`.

## Features

### ATS Engine (5 scoring dimensions)
- Keyword matching with 100+ alias mappings (JS = JavaScript, K8s = Kubernetes)
- Keyword placement quality (bullet context vs skills-only)
- Section structure validation
- Formatting compatibility checks
- Content relevance via TF-IDF cosine similarity

### AI Detection Engine (12 independent signals)
1. Sentence length variance
2. Consecutive length similarity
3. Opening word repetition (with synonym group detection)
4. Banned phrase density (50+ phrases)
5. Banned word density (23+ AI-flagged words)
6. Structure uniformity (8 structure types)
7. Round number usage
8. AI sentence pattern matching
9. Metric saturation
10. Summary adjective density
11. Transitional word overuse
12. Vocabulary predictability

### Fix Generator
- Prioritized suggestions (critical to low)
- Estimated score impact per fix
- Specific rewrite guidance
- Max 25 fixes to avoid overwhelm

## Tech Stack

- **Backend:** Python 3.12, FastAPI, spaCy, scikit-learn, pdfplumber
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts
- **Infrastructure:** Docker, GitHub Actions CI

## Testing

```bash
cd backend
pytest -v                          # Run all tests
pytest --cov=app --cov-report=html # Coverage report (80%+)
```

## License

MIT
