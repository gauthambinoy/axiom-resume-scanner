from fastapi import APIRouter, UploadFile, File, Form, Query, Depends
from fastapi.responses import JSONResponse, Response

from app.models.schemas import (
    ScanRequest,
    ScanResponse,
    CompareRequest,
    CompareResponse,
    QuickScanResponse,
    HealthResponse,
    StatsResponse,
    KeywordExtractionResponse,
    BannedPhrasesResponse,
    HumanizeRequest,
    HumanizeResponse,
    ErrorResponse,
)
import os

from app.engines.constants import BANNED_PHRASES, BANNED_EXTENDED_WORDS, AI_STRUCTURE_PATTERNS
from app.services.export_service import generate_pdf_report
from app.engines.keyword_extractor import KeywordExtractor
from app.api.dependencies import get_scan_service
from app.services.scan_service import ScanService
from app.utils.exceptions import InvalidFileError, ResumeShieldError
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["ResumeShield"])


@router.post(
    "/scan",
    response_model=ScanResponse,
    summary="Scan resume against job description",
    description="Performs full ATS compatibility and AI detection analysis",
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
async def scan_resume(
    request: ScanRequest,
    service: ScanService = Depends(get_scan_service),
) -> ScanResponse:
    return await service.scan(request.resume_text, request.jd_text, mode=request.mode)


@router.post(
    "/export/pdf",
    summary="Export scan results as PDF report",
    description="Runs a full scan and returns a downloadable PDF analysis report",
    responses={400: {"model": ErrorResponse}},
)
async def export_pdf(
    request: ScanRequest,
    service: ScanService = Depends(get_scan_service),
) -> Response:
    result = await service.scan(request.resume_text, request.jd_text, mode=request.mode)
    pdf_bytes = generate_pdf_report(result.model_dump())
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resumeshield-report.pdf"},
    )


@router.post(
    "/scan/file",
    response_model=ScanResponse,
    summary="Scan uploaded resume file against job description",
    description="Accepts PDF or DOCX file upload",
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
)
async def scan_file(
    file: UploadFile = File(..., description="PDF or DOCX resume file"),
    jd_text: str = Form("", max_length=8000, description="Job description text"),
    mode: str = Form("resume", description="Scan mode: resume, essay, blog, email, general"),
    service: ScanService = Depends(get_scan_service),
) -> ScanResponse:
    content_type = file.content_type or ""
    allowed = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    filename = file.filename or "upload"

    # Also allow by extension
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if content_type not in allowed and ext not in {"pdf", "docx"}:
        raise InvalidFileError(f"File type '{content_type}' not supported. Upload PDF or DOCX.")

    file_bytes = await file.read()
    return await service.scan("", jd_text, file_bytes=file_bytes, filename=filename, mode=mode)


@router.post(
    "/scan/bulk",
    summary="Bulk scan multiple resume files",
    description="Accepts up to 10 PDF/DOCX files for batch scanning",
)
async def scan_bulk(
    files: list[UploadFile] = File(..., description="PDF or DOCX resume files (max 10)"),
    jd_text: str = Form("", description="Job description text"),
    mode: str = Form("resume", description="Scan mode"),
    service: ScanService = Depends(get_scan_service),
):
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    results = []
    for file in files[:10]:  # Max 10 files
        content_type = file.content_type or ""
        filename = file.filename or "upload"
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if content_type not in allowed_types and ext not in {"pdf", "docx"}:
            results.append({"filename": filename, "error": "Unsupported file type"})
            continue
        try:
            file_bytes = await file.read()
            scan_result = await service.scan(
                "", jd_text, file_bytes=file_bytes, filename=filename, mode=mode,
            )
            results.append({"filename": filename, "result": scan_result.model_dump()})
        except Exception as e:
            results.append({"filename": filename, "error": str(e)})
    return {"results": results, "total": len(results)}


@router.post(
    "/scan/quick",
    response_model=QuickScanResponse,
    summary="Quick scan for fast re-checks",
    description="Lightweight scan returning only key scores",
)
async def quick_scan(
    request: ScanRequest,
    service: ScanService = Depends(get_scan_service),
) -> QuickScanResponse:
    return await service.quick_scan(request.resume_text, request.jd_text)


@router.post(
    "/compare",
    response_model=CompareResponse,
    summary="Compare two resume versions",
    description="Side-by-side comparison of before and after resume edits",
)
async def compare_resumes(
    request: CompareRequest,
    service: ScanService = Depends(get_scan_service),
) -> CompareResponse:
    return await service.compare(request.resume_before, request.resume_after, request.jd_text)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
)
async def health_check() -> HealthResponse:
    spacy_ok = False
    try:
        import spacy
        spacy.load("en_core_web_sm")
        spacy_ok = True
    except Exception:
        pass

    nltk_ok = False
    try:
        import nltk
        nltk.data.find("tokenizers/punkt_tab")
        nltk_ok = True
    except Exception:
        pass

    # Humanizer works without API key (rule-based), but ML layer needs HF key
    humanizer_ok = True  # Always available — rule-based transforms need no API key

    return HealthResponse(
        status="healthy",
        version="2.0.0",
        engines={"spacy": spacy_ok, "nltk": nltk_ok, "humanizer": humanizer_ok},
    )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Global scan statistics",
)
async def get_stats(
    service: ScanService = Depends(get_scan_service),
) -> StatsResponse:
    stats = service.get_stats()
    return StatsResponse(**stats)


@router.get(
    "/keywords/extract",
    response_model=KeywordExtractionResponse,
    summary="Extract keywords from job description",
)
async def extract_keywords(
    jd_text: str = Query(..., min_length=50, max_length=8000, description="Job description text"),
) -> KeywordExtractionResponse:
    extractor = KeywordExtractor()
    result = extractor.extract(jd_text)
    return KeywordExtractionResponse(
        technical_skills=result.technical_skills,
        soft_skills=result.soft_skills,
        tools_and_platforms=result.tools_and_platforms,
        action_verbs=result.action_verbs,
        domain_terms=result.domain_terms,
        certifications=result.certifications,
        all_keywords=result.all_keywords,
        priority_keywords=result.priority_keywords,
    )


@router.post(
    "/humanize",
    response_model=HumanizeResponse,
    summary="Humanize AI-detected resume text",
    description="Rewrites AI-flagged resume text to be undetectable by AI detectors using Claude API",
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
async def humanize_text(
    request: HumanizeRequest,
    service: ScanService = Depends(get_scan_service),
) -> HumanizeResponse:
    result = await service.humanize(request.resume_text, request.jd_text, tone=request.tone)
    return HumanizeResponse(
        original_text=result.original_text,
        humanized_text=result.humanized_text,
        original_ai_score=result.original_ai_score,
        new_ai_score=result.new_ai_score,
        improvement=result.improvement,
        retries_used=result.retries_used,
        success=result.success,
    )


@router.get(
    "/modes",
    summary="Get available scan modes and humanizer tones",
)
async def get_modes():
    return {
        "modes": [
            {"id": "resume", "label": "Resume", "requires_jd": True},
            {"id": "essay", "label": "Essay", "requires_jd": False},
            {"id": "blog", "label": "Blog Post", "requires_jd": False},
            {"id": "email", "label": "Email", "requires_jd": False},
            {"id": "general", "label": "General Text", "requires_jd": False},
        ],
        "tones": [
            {"id": "formal", "label": "Formal"},
            {"id": "casual", "label": "Casual"},
            {"id": "academic", "label": "Academic"},
            {"id": "professional", "label": "Professional"},
            {"id": "creative", "label": "Creative"},
        ],
    }


@router.get(
    "/banned-phrases",
    response_model=BannedPhrasesResponse,
    summary="Get all banned phrases and words",
    description="Returns lists used for real-time highlighting in the frontend",
)
async def get_banned_phrases() -> BannedPhrasesResponse:
    return BannedPhrasesResponse(
        banned_phrases=BANNED_PHRASES,
        banned_words=sorted(BANNED_EXTENDED_WORDS),
        ai_patterns=AI_STRUCTURE_PATTERNS,
    )
