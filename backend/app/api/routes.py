from fastapi import APIRouter, UploadFile, File, Form, Query, Depends
from fastapi.responses import JSONResponse

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
    ErrorResponse,
)
from app.engines.constants import BANNED_PHRASES, BANNED_EXTENDED_WORDS, AI_STRUCTURE_PATTERNS
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
    return await service.scan(request.resume_text, request.jd_text)


@router.post(
    "/scan/file",
    response_model=ScanResponse,
    summary="Scan uploaded resume file against job description",
    description="Accepts PDF or DOCX file upload",
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
)
async def scan_file(
    file: UploadFile = File(..., description="PDF or DOCX resume file"),
    jd_text: str = Form(..., min_length=50, max_length=8000, description="Job description text"),
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
    return await service.scan("", jd_text, file_bytes=file_bytes, filename=filename)


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

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        engines={"spacy": spacy_ok, "nltk": nltk_ok},
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
