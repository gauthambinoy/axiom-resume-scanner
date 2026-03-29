from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# --- Request Models ---

class ScanRequest(BaseModel):
    resume_text: str = Field(..., min_length=100, max_length=15000, description="Resume text content")
    jd_text: str = Field("", min_length=0, max_length=8000, description="Job description text")
    mode: str = Field("resume", description="Scan mode: resume, essay, blog, email, general")

    model_config = ConfigDict(json_schema_extra={
        "examples": [{
            "resume_text": "John Doe\njohn@example.com\n\nExperience\n- Built microservices with Python...",
            "jd_text": "We are looking for a Senior Python Developer with experience in FastAPI...",
            "mode": "resume"
        }]
    })


class CompareRequest(BaseModel):
    resume_before: str = Field(..., min_length=100, max_length=15000, description="Original resume text")
    resume_after: str = Field(..., min_length=100, max_length=15000, description="Updated resume text")
    jd_text: str = Field(..., min_length=50, max_length=8000, description="Job description text")


# --- Response Models ---

class KeywordMatchResponse(BaseModel):
    keyword: str = Field(..., description="The matched keyword")
    found_in_sections: list[str] = Field(default_factory=list, description="Sections where keyword was found")
    frequency_in_resume: int = Field(0, description="How many times the keyword appears")


class ATSScoreResponse(BaseModel):
    overall_score: int = Field(0, ge=0, le=100, description="Overall ATS compatibility score")
    keyword_match_score: int = Field(0, description="Keyword match score (0-100)")
    keyword_placement_score: int = Field(0, description="Keyword placement quality score")
    section_score: int = Field(0, description="Section structure score")
    formatting_score: int = Field(0, description="Formatting compatibility score")
    relevance_score: int = Field(0, description="Content relevance score")
    matched_keywords: list[KeywordMatchResponse] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    skills_only_keywords: list[str] = Field(default_factory=list)
    section_warnings: list[str] = Field(default_factory=list)
    formatting_warnings: list[str] = Field(default_factory=list)
    grade: str = Field("F", description="Letter grade A+ through F")


class SignalResponse(BaseModel):
    name: str = Field(..., description="Signal name")
    score: float = Field(0, description="Signal score")
    max_score: float = Field(8.33, description="Maximum possible score for this signal")
    percentage: float = Field(0, description="Score as percentage of max")
    details: str = Field("", description="Human-readable explanation")
    flagged_items: list[str] = Field(default_factory=list)


class BulletAnalysisResponse(BaseModel):
    text: str = Field(..., description="Bullet text")
    word_count: int = Field(0, description="Number of words")
    structure_type: str = Field("", description="Classified structure type")
    first_word: str = Field("", description="First word of bullet")
    flags: list[str] = Field(default_factory=list, description="Issues found")
    ai_risk: str = Field("clean", description="Risk level: clean, suspicious, flagged")
    diff_from_previous: int | None = Field(None, description="Word count difference from previous bullet")


class SummaryAnalysisResponse(BaseModel):
    adjective_count: int = Field(0)
    adjectives_found: list[str] = Field(default_factory=list)
    starts_with_adjective: bool = Field(False)
    word_count: int = Field(0)
    has_years_experience: bool = Field(False)
    has_seniority_label: bool = Field(False)


class HeatmapItemResponse(BaseModel):
    text: str
    risk: float
    flags: list[str] = Field(default_factory=list)
    color: str = "green"


class TextAnalyticsResponse(BaseModel):
    word_count: int = 0
    character_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    avg_sentence_length: float = 0.0
    avg_word_length: float = 0.0
    vocabulary_richness: float = 0.0
    longest_sentence: int = 0
    shortest_sentence: int = 0
    top_words: list[list] = Field(default_factory=list)


class AIDetectionResponse(BaseModel):
    overall_score: float = Field(0, ge=0, le=100, description="AI detection score (0=human, 100=AI)")
    risk_level: str = Field("LOW", description="Risk level: LOW, MODERATE, HIGH, CRITICAL")
    signals: list[SignalResponse] = Field(default_factory=list)
    per_bullet_analysis: list[BulletAnalysisResponse] = Field(default_factory=list)
    summary_analysis: SummaryAnalysisResponse = Field(default_factory=SummaryAnalysisResponse)
    top_issues: list[str] = Field(default_factory=list)
    heatmap: list[HeatmapItemResponse] = Field(default_factory=list)


class FixResponse(BaseModel):
    category: str = Field(..., description="Fix category: ats_keyword, ai_detection, section, formatting")
    priority: str = Field(..., description="Priority: critical, high, medium, low")
    title: str = Field(..., description="Short description of the fix")
    description: str = Field(..., description="Detailed fix instruction")
    affected_bullets: list[int] = Field(default_factory=list)
    estimated_impact: str = Field("", description="Estimated score impact")


class CombinedScoreResponse(BaseModel):
    interview_readiness_score: int = Field(0, description="Combined readiness score 0-100")
    readiness_level: str = Field("AT_RISK", description="INTERVIEW_READY, NEEDS_WORK, AT_RISK")
    competitor_percentile: int = Field(50, description="Percentile ranking vs other applicants")
    ats_weight: float = Field(0.6)
    ai_weight: float = Field(0.4)


class ReadabilityResponse(BaseModel):
    flesch_kincaid_grade: float = Field(0.0, description="Flesch-Kincaid readability grade level")
    reading_time_seconds: int = Field(0, description="Estimated reading time in seconds")
    word_count: int = Field(0, description="Total word count")
    sentence_count: int = Field(0, description="Total sentence count")
    avg_sentence_length: float = Field(0.0, description="Average words per sentence")
    avg_word_length: float = Field(0.0, description="Average characters per word")
    vocabulary_richness: float = Field(0.0, description="Unique words / total words ratio")


class ScanMetadata(BaseModel):
    processing_time_ms: int = Field(0, description="Total processing time in milliseconds")
    engines_used: list[str] = Field(default_factory=list)
    degraded_mode: bool = Field(False, description="Whether any engine fell back to degraded mode")
    warnings: list[str] = Field(default_factory=list)


class ScanResponse(BaseModel):
    scan_id: str = Field(..., description="Unique scan identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ats_score: ATSScoreResponse = Field(default_factory=ATSScoreResponse)
    ai_score: AIDetectionResponse = Field(default_factory=AIDetectionResponse)
    fixes: list[FixResponse] = Field(default_factory=list)
    combined: CombinedScoreResponse = Field(default_factory=CombinedScoreResponse)
    readability: ReadabilityResponse = Field(default_factory=ReadabilityResponse)
    text_analytics: TextAnalyticsResponse = Field(default_factory=TextAnalyticsResponse)
    metadata: ScanMetadata = Field(default_factory=ScanMetadata)


class QuickScanResponse(BaseModel):
    scan_id: str
    ats_keyword_score: int = 0
    ai_detection_score: float = 0
    readiness_level: str = "AT_RISK"
    processing_time_ms: int = 0


class CompareResponse(BaseModel):
    before: ScanResponse
    after: ScanResponse
    ats_change: int = Field(0, description="ATS score change (positive = improvement)")
    ai_change: float = Field(0, description="AI score change (negative = improvement)")
    readiness_change: int = Field(0, description="Readiness score change")
    improved_keywords: list[str] = Field(default_factory=list)
    still_missing: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    engines: dict[str, bool] = Field(default_factory=dict)


class StatsResponse(BaseModel):
    total_scans: int = 0
    avg_ats_score: float = 0
    avg_ai_score: float = 0
    scans_today: int = 0


class KeywordExtractionResponse(BaseModel):
    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    tools_and_platforms: list[str] = Field(default_factory=list)
    action_verbs: list[str] = Field(default_factory=list)
    domain_terms: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    all_keywords: list[str] = Field(default_factory=list)
    priority_keywords: list[str] = Field(default_factory=list)


class BannedPhrasesResponse(BaseModel):
    banned_phrases: list[str] = Field(default_factory=list)
    banned_words: list[str] = Field(default_factory=list)
    ai_patterns: list[str] = Field(default_factory=list)


class HumanizeRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=15000, description="Resume text to humanize")
    jd_text: str = Field("", max_length=8000, description="Optional: job description to preserve relevant keywords")
    mode: str = Field("general", description="Text mode: resume, essay, blog, email, general")
    tone: str = Field("professional", description="Output tone: formal, casual, academic, professional, creative")


class HumanizeResponse(BaseModel):
    original_text: str = Field(..., description="Original input text")
    humanized_text: str = Field(..., description="Rewritten human-sounding text")
    original_ai_score: float = Field(0, description="AI detection score before humanization")
    new_ai_score: float = Field(0, description="AI detection score after humanization")
    improvement: float = Field(0, description="Score reduction (positive = better)")
    retries_used: int = Field(0, description="Number of retry iterations used")
    success: bool = Field(False, description="Whether the text passed AI detection (<30)")


class ErrorResponse(BaseModel):
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict | None = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
