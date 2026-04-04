# ResumeShield Architecture

This document describes the technical architecture of ResumeShield — a dual-axis resume scanner that evaluates ATS keyword compatibility and AI-generated text detection simultaneously.

---

## Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Browser (React + TS)                      │
│  Landing → Scanner → Results → History → Bulk Upload         │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTPS (REST)
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python)                    │
│                                                              │
│  ┌─────────────────┐         ┌────────────────────────────┐  │
│  │   ATS Engine    │         │    AI Detection Engine     │  │
│  │  (5 dimensions) │         │     (19 signals)           │  │
│  └────────┬────────┘         └─────────────┬──────────────┘  │
│           │                                │                  │
│  ┌────────▼──────────────────────────────▼──────────────┐    │
│  │                  Scan Service                         │    │
│  │   Orchestrates: parse → extract → score → combine    │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌───────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │    Section    │  │   Keyword   │  │   Fix Generator  │   │
│  │    Parser     │  │  Extractor  │  │                  │   │
│  └───────────────┘  └─────────────┘  └──────────────────┘   │
│  ┌───────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │  PDF Parser   │  │   Grammar   │  │   Humanizer      │   │
│  │ (pdfplumber)  │  │   Engine    │  │   Engine         │   │
│  └───────────────┘  └─────────────┘  └──────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## Dual-Axis Scanning Architecture

ResumeShield is the first tool that checks a resume on **two axes simultaneously**:

| Axis | Engine | Output |
|------|--------|--------|
| ATS compatibility | `ATSEngine` | Score 0–100, grade A+–F |
| AI detection | `AIDetectionEngine` | Score 0–100, risk level LOW/MODERATE/HIGH/CRITICAL |

The `ScoreNormalizer` combines both axes into an **Interview Readiness Score** (0–100) with a `INTERVIEW_READY / NEEDS_WORK / AT_RISK` readiness level.

---

## Backend Engine Design

### Pipeline (per scan request)

```
resume_text + jd_text
        │
        ▼
  SectionParser.parse()
        │  → SectionParseResult (sections, bullets, contact info, word count)
        ▼
  KeywordExtractor.extract(jd_text)
        │  → KeywordExtractionResult (technical skills, soft skills, tools, etc.)
        ▼
  ATSEngine.score()          AIDetectionEngine.analyze()
        │                              │
        └──────────┬───────────────────┘
                   ▼
         ScoreNormalizer.combine()
                   │
                   ▼
         FixGenerator.generate()
                   │
                   ▼
           ScanResponse (JSON)
```

### ATS Engine (`app/engines/ats_engine.py`)

Scores across five dimensions:

1. **Keyword Match Score** — Does the resume contain the keywords from the JD? Alias mappings (JS → JavaScript, K8s → Kubernetes) ensure abbreviations count. 100+ aliases configured in `constants.py`.
2. **Keyword Placement Score** — Are keywords buried in a skills list or demonstrated in bullet context? Bullet mentions score higher than skills-section-only.
3. **Section Score** — Are all required sections present? (Experience, Education, Skills). Checks for REQUIRED_SECTIONS and RECOMMENDED_SECTIONS.
4. **Formatting Score** — Detects formatting patterns that confuse ATS parsers (tables, columns, graphics, non-standard characters).
5. **Relevance Score** — TF-IDF cosine similarity between the resume text and the job description to measure semantic alignment.

### AI Detection Engine (`app/engines/ai_detection_engine.py`)

Analyses 19 independent signals (12 original + 5 advanced + 2 ML-based):

1. Sentence length variance — AI text is unusually uniform in sentence length
2. Consecutive length similarity — repetitive sentence lengths in adjacent bullets
3. Opening word repetition — "Developed X, Implemented Y, Developed Z" triggers synonym group detection
4. Banned phrase density — 50+ phrases flagged (e.g. "proven track record", "results-driven")
5. Banned word density — 23+ words flagged (e.g. "leverage", "passionate", "dynamic")
6. Structure uniformity — 8 bullet structure types; high uniformity = AI signal
7. Round number usage — AI models over-use round numbers (30%, 50%, 100%)
8. AI sentence pattern matching — regex patterns for known AI sentence templates
9. Metric saturation — too many metrics per bullet (AI overclaims)
10. Summary adjective density — "passionate, results-driven, dynamic" in summary
11. Transitional word overuse — "Furthermore", "Additionally" as bullet openers
12. Vocabulary predictability — bigram/trigram predictability heuristic
13–17. Advanced signals (perplexity estimation, burstiness, semantic coherence)
18–19. ML-based signals via HuggingFace API (optional — gracefully disabled when key absent)

Each signal returns a score between 0 and `MAX_SIGNAL_SCORE` (≈5.26). They sum to the overall AI detection score (0–100).

### Section Parser (`app/engines/section_parser.py`)

Identifies structural components of the resume:
- Detects section headers (ALL CAPS, Title Case, or known patterns)
- Extracts `BulletPoint` objects with metadata: `word_count`, `first_word`, `has_metric`, `section`
- Extracts `ContactInfo` (name, email, phone, LinkedIn, GitHub)
- Identifies `ExperienceEntry` blocks (company, title, date range, bullets)

### Keyword Extractor (`app/engines/keyword_extractor.py`)

Parses a job description into structured keyword sets:
- Technical skills, soft skills, tools and platforms, action verbs, domain terms, certifications
- Uses spaCy (`en_core_web_sm`) when available, falls back to regex extraction
- Builds `priority_keywords` list by weighting by frequency and section prominence

### Fix Generator (`app/engines/fix_generator.py`)

Takes `ATSScoreResult` + `AIDetectionResult` and generates prioritised actionable suggestions:
- Up to 25 fixes, sorted by estimated score impact
- Priority levels: CRITICAL → HIGH → MEDIUM → LOW
- Each fix includes: issue description, specific rewrite guidance, and estimated impact

---

## Frontend Data Flow

```
User input (textarea / file drop)
        │
        ▼
  useScan() hook
  ├── validateResumeText() / validateJDText()   (client-side)
  ├── POST /api/v1/scan  (axios)
  └── ScanResponse → local state
        │
        ▼
  ResultsDashboard
  ├── ScoreGauge (ATS score)
  ├── ScoreGauge (AI score, inverted colour scale)
  ├── ATSPanel (keyword grid, section warnings)
  ├── AIDetectionPanel (signal breakdown, heatmap)
  ├── FixSuggestions (prioritised fix list)
  └── ExportButton (POST /api/v1/export/pdf)
```

Real-time pre-scan:
- `ScannerPage` uses a debounced call to `POST /api/v1/scan/quick` (text only, no JD required) to show a live AI risk indicator as the user types.

Scan history:
- Results are persisted to `localStorage` via `utils/history.ts`.
- `HistoryDashboard` component allows re-viewing and comparing past scans.

---

## Deployment Architecture

```
                     Vercel (CDN)
                  ┌──────────────┐
  Browser ──────▶ │  React SPA   │
                  │  (frontend/) │
                  └──────┬───────┘
                         │ API calls
                         ▼
                  ┌──────────────┐
                  │ Render.com   │
                  │  FastAPI     │
                  │ (backend/)   │
                  └──────────────┘
```

- **Frontend** — Deployed to Vercel. Static build via `npm run build` (Vite). No server-side rendering.
- **Backend** — Deployed to Render.com as a Docker container. Configuration in `render.yaml`. The `Dockerfile` installs Python deps, downloads spaCy and NLTK data at build time.
- **CI** — GitHub Actions runs on push to `main`. `backend-ci.yml` runs pytest with coverage checks. `frontend-ci.yml` runs TypeScript type checking and the production build.
- **Environment** — All secrets (HuggingFace API key, AWS keys) are injected via environment variables on Render. Copy `backend/.env.example` to `backend/.env` for local development.

### Key configuration files

| File | Purpose |
|------|---------|
| `render.yaml` | Render deployment spec |
| `vercel.json` | Vercel routing (SPA fallback, API proxy) |
| `docker-compose.yml` | Local full-stack environment |
| `backend/Dockerfile` | Production backend image |
| `frontend/Dockerfile` | Production frontend image |
| `backend/.env.example` | Environment variable template |

