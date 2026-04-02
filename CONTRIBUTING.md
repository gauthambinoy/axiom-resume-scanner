# Contributing to ResumeShield

## Setup
```bash
# Backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## Architecture
ResumeShield uses a dual-axis scanning approach:
- **ATS Scanner**: Analyzes keywords, formatting, structure against job descriptions
- **AI Detector**: 12+ signals detect AI-generated content in resumes

## Adding New Detection Signals
1. Create signal function in the detection module
2. Register in the signal pipeline
3. Add tests and calibrate weights
4. Update signal count in README

## Code Style
- **Python**: PEP 8, enforced by `ruff`
- **TypeScript**: ESLint + Prettier
- **Commits**: Conventional commits
