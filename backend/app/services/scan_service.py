import time
import uuid

from app.engines.keyword_extractor import KeywordExtractor
from app.engines.section_parser import SectionParser
from app.engines.ats_engine import ATSEngine
from app.engines.ai_detection_engine import AIDetectionEngine
from app.engines.fix_generator import FixGenerator
from app.engines.pdf_parser import PDFParser
from app.engines.scoring import ScoreNormalizer
from app.engines.humanizer_engine import HumanizerEngine, HumanizeRequest, HumanizeResult
from app.models.schemas import (
    ScanResponse,
    ATSScoreResponse,
    AIDetectionResponse,
    SignalResponse,
    BulletAnalysisResponse,
    SummaryAnalysisResponse,
    FixResponse,
    CombinedScoreResponse,
    ScanMetadata,
    KeywordMatchResponse,
    QuickScanResponse,
    CompareResponse,
)
from app.utils.text_processing import clean_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScanService:
    def __init__(self) -> None:
        self._keyword_extractor = KeywordExtractor()
        self._section_parser = SectionParser()
        self._ats_engine = ATSEngine()
        self._ai_engine = AIDetectionEngine()
        self._fix_generator = FixGenerator()
        self._pdf_parser = PDFParser()
        self._score_normalizer = ScoreNormalizer()
        self._humanizer = HumanizerEngine()
        self._scan_count = 0
        self._total_ats = 0.0
        self._total_ai = 0.0
        self._today_count = 0

    async def scan(
        self,
        resume_text: str,
        jd_text: str,
        file_bytes: bytes | None = None,
        filename: str = "",
    ) -> ScanResponse:
        start = time.time()
        scan_id = str(uuid.uuid4())
        warnings: list[str] = []
        engines_used: list[str] = []
        degraded = False

        try:
            # Step 1: PDF extraction if file provided
            if file_bytes:
                try:
                    pdf_result = self._pdf_parser.extract(file_bytes, filename)
                    resume_text = pdf_result.text
                    warnings.extend(pdf_result.warnings)
                    engines_used.append("pdf_parser")
                except Exception as e:
                    logger.error("PDF parsing failed", error=str(e))
                    raise

            # Step 2-4: Clean and process
            cleaned_resume = clean_text(resume_text)
            cleaned_jd = clean_text(jd_text)

            # Step 5: Extract keywords
            keywords = self._keyword_extractor.extract(cleaned_jd)
            engines_used.append("keyword_extractor")
            if keywords.warning:
                warnings.append(keywords.warning)

            # Step 6: Parse sections
            sections = self._section_parser.parse(cleaned_resume)
            engines_used.append("section_parser")
            warnings.extend(sections.warnings)

            # Step 7: ATS scoring
            ats_result = self._ats_engine.score(cleaned_resume, cleaned_jd, sections, keywords)
            engines_used.append("ats_engine")

            # Step 8: AI detection
            ai_result = self._ai_engine.analyze(cleaned_resume, sections, sections.bullets)
            engines_used.append("ai_detection_engine")

            # Step 9: Generate fixes
            fixes = self._fix_generator.generate(ats_result, ai_result, sections)
            engines_used.append("fix_generator")

            # Step 10: Combined scoring
            combined = self._score_normalizer.combine(ats_result, ai_result)
            engines_used.append("score_normalizer")

            # Track stats
            self._scan_count += 1
            self._today_count += 1
            self._total_ats += ats_result.overall_score
            self._total_ai += ai_result.overall_score

            elapsed_ms = int((time.time() - start) * 1000)

            return self._build_response(
                scan_id, ats_result, ai_result, fixes, combined,
                elapsed_ms, engines_used, degraded, warnings, sections,
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start) * 1000)
            logger.error("Scan pipeline failed", scan_id=scan_id, error=str(e))
            raise

    async def quick_scan(self, resume_text: str, jd_text: str) -> QuickScanResponse:
        start = time.time()
        scan_id = str(uuid.uuid4())

        cleaned_resume = clean_text(resume_text)
        cleaned_jd = clean_text(jd_text)

        keywords = self._keyword_extractor.extract(cleaned_jd)
        sections = self._section_parser.parse(cleaned_resume)

        # Only keyword match + AI overall
        matched = 0
        for kw in keywords.all_keywords:
            if kw.lower() in cleaned_resume.lower():
                matched += 1
        kw_score = round((matched / max(len(keywords.all_keywords), 1)) * 100)

        ai_result = self._ai_engine.analyze(cleaned_resume, sections, sections.bullets)
        combined = self._score_normalizer.combine(
            type("ATS", (), {"overall_score": kw_score, "grade": "C"})(),  # type: ignore[arg-type]
            ai_result,
        )

        elapsed_ms = int((time.time() - start) * 1000)

        return QuickScanResponse(
            scan_id=scan_id,
            ats_keyword_score=kw_score,
            ai_detection_score=round(ai_result.overall_score, 1),
            readiness_level=combined.readiness_level,
            processing_time_ms=elapsed_ms,
        )

    async def compare(
        self, resume_before: str, resume_after: str, jd_text: str,
    ) -> CompareResponse:
        before = await self.scan(resume_before, jd_text)
        after = await self.scan(resume_after, jd_text)

        before_missing = set(before.ats_score.missing_keywords)
        after_missing = set(after.ats_score.missing_keywords)

        return CompareResponse(
            before=before,
            after=after,
            ats_change=after.ats_score.overall_score - before.ats_score.overall_score,
            ai_change=round(after.ai_score.overall_score - before.ai_score.overall_score, 1),
            readiness_change=after.combined.interview_readiness_score - before.combined.interview_readiness_score,
            improved_keywords=list(before_missing - after_missing),
            still_missing=list(after_missing),
        )

    async def humanize(self, resume_text: str, jd_text: str = "") -> HumanizeResult:
        """Run AI detection on the text, then humanize flagged content."""
        cleaned_resume = clean_text(resume_text)

        # First, analyze to find what needs fixing
        sections = self._section_parser.parse(cleaned_resume)
        ai_result = self._ai_engine.analyze(cleaned_resume, sections, sections.bullets)

        # Build humanize request with specific signal data
        flagged_signals = [
            f"{s.name}: {s.details}"
            for s in ai_result.signals
            if s.score >= 2.0
        ]
        flagged_phrases = []
        flagged_words = []
        for s in ai_result.signals:
            if s.name == "Banned Phrase Density":
                flagged_phrases = s.flagged_items
            elif s.name == "Banned Word Density":
                flagged_words = s.flagged_items

        request = HumanizeRequest(
            text=cleaned_resume,
            ai_score=ai_result.overall_score,
            flagged_signals=flagged_signals,
            flagged_phrases=flagged_phrases,
            flagged_words=flagged_words,
            jd_text=jd_text,
        )

        return await self._humanizer.humanize(request)

    def get_stats(self) -> dict[str, int | float]:
        return {
            "total_scans": self._scan_count,
            "avg_ats_score": round(self._total_ats / max(self._scan_count, 1), 1),
            "avg_ai_score": round(self._total_ai / max(self._scan_count, 1), 1),
            "scans_today": self._today_count,
        }

    def _build_response(
        self, scan_id, ats_result, ai_result, fixes, combined,
        elapsed_ms, engines_used, degraded, warnings, sections,
    ) -> ScanResponse:
        # ATS response
        ats_resp = ATSScoreResponse(
            overall_score=ats_result.overall_score,
            keyword_match_score=ats_result.keyword_match_score,
            keyword_placement_score=ats_result.keyword_placement_score,
            section_score=ats_result.section_score,
            formatting_score=ats_result.formatting_score,
            relevance_score=ats_result.relevance_score,
            matched_keywords=[
                KeywordMatchResponse(
                    keyword=km.keyword,
                    found_in_sections=km.found_in_sections,
                    frequency_in_resume=km.frequency_in_resume,
                ) for km in ats_result.matched_keywords
            ],
            missing_keywords=ats_result.missing_keywords,
            skills_only_keywords=ats_result.skills_only_keywords,
            section_warnings=ats_result.section_warnings,
            formatting_warnings=ats_result.formatting_warnings,
            grade=ats_result.grade,
        )

        # AI response
        signal_responses = []
        for s in ai_result.signals:
            signal_responses.append(SignalResponse(
                name=s.name,
                score=round(s.score, 2),
                max_score=round(s.max_score, 2),
                percentage=round((s.score / s.max_score) * 100, 1) if s.max_score > 0 else 0,
                details=s.details,
                flagged_items=s.flagged_items,
            ))

        bullet_responses = []
        prev_wc = None
        for ba in ai_result.per_bullet_analysis:
            diff = abs(ba.word_count - prev_wc) if prev_wc is not None else None
            bullet_responses.append(BulletAnalysisResponse(
                text=ba.text,
                word_count=ba.word_count,
                structure_type=ba.structure_type,
                first_word=ba.first_word,
                flags=ba.flags,
                ai_risk=ba.ai_risk,
                diff_from_previous=diff,
            ))
            prev_wc = ba.word_count

        sa = ai_result.summary_analysis
        summary_resp = SummaryAnalysisResponse(
            adjective_count=sa.adjective_count,
            adjectives_found=sa.adjectives_found,
            starts_with_adjective=sa.starts_with_adjective,
            word_count=sa.word_count,
            has_years_experience=sa.has_years_experience,
            has_seniority_label=sa.has_seniority_label,
        )

        ai_resp = AIDetectionResponse(
            overall_score=round(ai_result.overall_score, 1),
            risk_level=ai_result.risk_level,
            signals=signal_responses,
            per_bullet_analysis=bullet_responses,
            summary_analysis=summary_resp,
            top_issues=ai_result.top_issues,
        )

        # Fixes
        fix_responses = [
            FixResponse(
                category=f.category,
                priority=f.priority,
                title=f.title,
                description=f.description,
                affected_bullets=f.affected_bullets,
                estimated_impact=f.impact,
            ) for f in fixes
        ]

        # Combined
        combined_resp = CombinedScoreResponse(
            interview_readiness_score=combined.interview_readiness_score,
            readiness_level=combined.readiness_level,
            competitor_percentile=combined.competitor_percentile,
            ats_weight=combined.ats_weight,
            ai_weight=combined.ai_weight,
        )

        return ScanResponse(
            scan_id=scan_id,
            ats_score=ats_resp,
            ai_score=ai_resp,
            fixes=fix_responses,
            combined=combined_resp,
            metadata=ScanMetadata(
                processing_time_ms=elapsed_ms,
                engines_used=engines_used,
                degraded_mode=degraded,
                warnings=warnings,
            ),
        )
