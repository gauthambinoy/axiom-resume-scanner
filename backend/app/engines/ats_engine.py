import re
from dataclasses import dataclass, field

from app.engines.constants import (
    KEYWORD_ALIASES,
    REVERSE_ALIASES,
    REQUIRED_SECTIONS,
    RECOMMENDED_SECTIONS,
)
from app.engines.keyword_extractor import KeywordExtractionResult
from app.engines.section_parser import SectionParseResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

GRADE_THRESHOLDS = [
    (90, "A+"), (80, "A"), (70, "B+"), (60, "B"),
    (50, "C+"), (40, "C"), (30, "D"), (0, "F"),
]


@dataclass
class KeywordMatch:
    keyword: str
    found_in_sections: list[str] = field(default_factory=list)
    frequency_in_resume: int = 0


@dataclass
class ATSScoreResult:
    overall_score: int = 0
    keyword_match_score: int = 0
    keyword_placement_score: int = 0
    section_score: int = 0
    formatting_score: int = 0
    relevance_score: int = 0
    matched_keywords: list[KeywordMatch] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    skills_only_keywords: list[str] = field(default_factory=list)
    section_warnings: list[str] = field(default_factory=list)
    formatting_warnings: list[str] = field(default_factory=list)
    grade: str = "F"


class ATSEngine:
    def __init__(self) -> None:
        self._nlp = None
        try:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        except (OSError, ImportError):
            pass

    def score(
        self,
        resume_text: str,
        jd_text: str,
        sections: SectionParseResult,
        keywords: KeywordExtractionResult,
    ) -> ATSScoreResult:
        try:
            result = ATSScoreResult()
            resume_lower = resume_text.lower()

            # 1. Keyword Match Score (35%)
            kw_score, matched, missing = self._score_keyword_match(
                resume_lower, keywords, sections
            )
            result.keyword_match_score = kw_score
            result.matched_keywords = matched
            result.missing_keywords = missing

            # 2. Keyword Placement Quality (20%)
            placement_score, skills_only = self._score_keyword_placement(
                matched, sections
            )
            result.keyword_placement_score = placement_score
            result.skills_only_keywords = skills_only

            # 3. Section Structure (15%)
            section_score, section_warnings = self._score_sections(sections)
            result.section_score = section_score
            result.section_warnings = section_warnings

            # 4. Formatting Compatibility (15%)
            format_score, format_warnings = self._score_formatting(resume_text, sections)
            result.formatting_score = format_score
            result.formatting_warnings = format_warnings

            # 5. Content Relevance (15%)
            relevance_score = self._score_relevance(resume_text, jd_text)
            result.relevance_score = relevance_score

            # Weighted combination
            overall = (
                kw_score * 0.35
                + placement_score * 0.20
                + section_score * 0.15
                + format_score * 0.15
                + relevance_score * 0.15
            )
            result.overall_score = min(100, max(0, round(overall)))

            # Grade
            for threshold, grade in GRADE_THRESHOLDS:
                if result.overall_score >= threshold:
                    result.grade = grade
                    break

            return result
        except Exception as e:
            logger.error("ATS scoring failed", error=str(e))
            return ATSScoreResult()

    def _score_keyword_match(
        self,
        resume_lower: str,
        keywords: KeywordExtractionResult,
        sections: SectionParseResult,
    ) -> tuple[int, list[KeywordMatch], list[str]]:
        all_kw = keywords.all_keywords
        if not all_kw:
            return 0, [], []

        matched: list[KeywordMatch] = []
        missing: list[str] = []

        for kw in all_kw:
            found = self._keyword_in_text(kw, resume_lower)
            if found:
                freq = self._count_keyword(kw, resume_lower)
                found_sections = self._find_keyword_sections(kw, sections)
                matched.append(KeywordMatch(
                    keyword=kw,
                    found_in_sections=found_sections,
                    frequency_in_resume=freq,
                ))
            else:
                missing.append(kw)

        # Order missing by priority from JD
        priority_set = set(keywords.priority_keywords)
        missing.sort(key=lambda k: (0 if k in priority_set else 1, k))

        score = round((len(matched) / len(all_kw)) * 100) if all_kw else 0
        return min(100, score), matched, missing

    def _keyword_in_text(self, keyword: str, text: str) -> bool:
        kw_lower = keyword.lower()
        # Direct match
        try:
            if re.search(rf"\b{re.escape(kw_lower)}\b", text):
                return True
        except re.error:
            if kw_lower in text:
                return True

        # Check aliases
        aliases = KEYWORD_ALIASES.get(kw_lower, [])
        for alias in aliases:
            try:
                if re.search(rf"\b{re.escape(alias.lower())}\b", text):
                    return True
            except re.error:
                if alias.lower() in text:
                    return True

        # Check reverse (if keyword is an alias, check canonical)
        canonical = REVERSE_ALIASES.get(kw_lower)
        if canonical:
            try:
                if re.search(rf"\b{re.escape(canonical)}\b", text):
                    return True
            except re.error:
                if canonical in text:
                    return True

        # Semantic similarity fallback using spaCy vectors
        if self._nlp and self._nlp.vocab.vectors.shape[0] > 0:
            try:
                kw_doc = self._nlp(kw_lower)
                # Check against text words for semantic match
                text_words = set(text.split())
                for word in text_words:
                    word_doc = self._nlp(word)
                    if kw_doc.has_vector and word_doc.has_vector:
                        similarity = kw_doc.similarity(word_doc)
                        if similarity >= 0.80:
                            return True
            except Exception:
                pass

        return False

    def _count_keyword(self, keyword: str, text: str) -> int:
        try:
            return len(re.findall(rf"\b{re.escape(keyword.lower())}\b", text))
        except re.error:
            return text.count(keyword.lower())

    def _find_keyword_sections(self, keyword: str, sections: SectionParseResult) -> list[str]:
        found_in: list[str] = []
        kw_lower = keyword.lower()
        for section_name, content in sections.section_content.items():
            content_lower = content.lower()
            try:
                if re.search(rf"\b{re.escape(kw_lower)}\b", content_lower):
                    found_in.append(section_name)
            except re.error:
                if kw_lower in content_lower:
                    found_in.append(section_name)
        return found_in

    def _score_keyword_placement(
        self,
        matched: list[KeywordMatch],
        sections: SectionParseResult,
    ) -> tuple[int, list[str]]:
        if not matched:
            return 0, []

        total_points = 0
        max_points = len(matched) * 3  # Best is 3 per keyword
        skills_only: list[str] = []

        skills_names = {"skills", "technical skills", "core skills", "key skills", "additional skills"}
        bullet_sections = {"experience", "work experience", "employment", "projects",
                          "professional experience", "work history", "relevant experience"}

        for km in matched:
            sections_lower = {s.lower() for s in km.found_in_sections}
            in_bullet_section = bool(sections_lower & bullet_sections)
            in_skills = bool(sections_lower & skills_names)
            in_summary = any("summary" in s or "objective" in s or "profile" in s for s in sections_lower)
            in_projects = "projects" in sections_lower

            if in_bullet_section:
                total_points += 3
            elif in_summary:
                total_points += 2
            elif in_projects:
                total_points += 2
            elif in_skills:
                total_points += 2
            else:
                total_points += 0

            if in_skills and not in_bullet_section and not in_summary and not in_projects:
                skills_only.append(km.keyword)

        score = round((total_points / max(max_points, 1)) * 100)
        return min(100, score), skills_only

    def _score_sections(self, sections: SectionParseResult) -> tuple[int, list[str]]:
        warnings: list[str] = []
        points = 0
        max_points = len(REQUIRED_SECTIONS) * 4 + len(RECOMMENDED_SECTIONS) * 2  # 22

        normalized_found = set()
        section_name_map = {
            "professional experience": "experience",
            "work experience": "experience",
            "work history": "experience",
            "relevant experience": "experience",
            "professional summary": "summary",
            "career objective": "objective",
            "core skills": "skills",
            "key skills": "skills",
            "additional skills": "skills",
            "technical skills": "skills",
        }

        for name in sections.sections_found:
            norm = section_name_map.get(name.lower(), name.lower())
            normalized_found.add(norm)

        # Check if contact info is present (substitute for "contact" section)
        if sections.contact_info.email or sections.contact_info.phone:
            normalized_found.add("contact")

        for req in REQUIRED_SECTIONS:
            if req in normalized_found:
                points += 4
            else:
                warnings.append(f"Missing required section: {req.title()}")

        for rec in RECOMMENDED_SECTIONS:
            if rec in normalized_found:
                points += 2

        score = round((points / max(max_points, 1)) * 100)
        return min(100, score), warnings

    def _score_formatting(self, text: str, sections: SectionParseResult) -> tuple[int, list[str]]:
        score = 100
        warnings: list[str] = []

        # Tables detected
        if re.search(r"(?:\|.*\|.*\|)", text) or re.search(r"\t{2,}", text):
            score -= 10
            warnings.append("Tables detected - many ATS systems cannot parse tables")

        # Image references
        if re.search(r"(?i)\[image\]|\.png|\.jpg|\.jpeg|\.gif|<img", text):
            score -= 10
            warnings.append("Image references detected - ATS cannot read images")

        # Column-like layout (lots of whitespace gaps in lines)
        column_lines = 0
        for line in text.split("\n"):
            if re.search(r"\S\s{4,}\S", line):
                column_lines += 1
        if column_lines > 5:
            score -= 5
            warnings.append("Multi-column layout detected - may confuse ATS parsers")

        # Special character overuse
        special_count = len(re.findall(r"[★☆●◆■□▲△▼▽♦♠♣♥→←↑↓✓✗✘]", text))
        if special_count > 10:
            score -= 5
            warnings.append("Excessive special characters may not be parsed by ATS")

        # Date consistency check
        date_formats_found: set[str] = set()
        if re.search(r"\b\d{1,2}/\d{4}\b", text):
            date_formats_found.add("MM/YYYY")
        if re.search(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}", text):
            date_formats_found.add("Month YYYY")
        if re.search(r"\b\d{4}-\d{2}\b", text):
            date_formats_found.add("YYYY-MM")
        if len(date_formats_found) <= 1:
            score += 5  # Consistent
        elif len(date_formats_found) > 1:
            warnings.append("Inconsistent date formats detected")

        # Standard section headers bonus
        if not sections.flat_text_mode and len(sections.sections_found) >= 4:
            score += 5

        return min(100, max(0, score)), warnings

    def _score_relevance(self, resume_text: str, jd_text: str) -> int:
        tfidf_score = 0
        semantic_score = 0

        # Method 1: TF-IDF cosine similarity (with bigrams for better matching)
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(
                stop_words="english",
                max_features=1000,
                ngram_range=(1, 2),  # Unigrams + bigrams for phrase-level matching
                sublinear_tf=True,   # Apply log normalization for better term weighting
            )
            tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
            tfidf_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
        except Exception:
            # Fallback: simple word overlap
            resume_words = set(resume_text.lower().split())
            jd_words = set(jd_text.lower().split())
            if jd_words:
                overlap = len(resume_words & jd_words)
                tfidf_score = (overlap / len(jd_words)) * 100

        # Method 2: Semantic similarity via spaCy vectors
        if self._nlp:
            try:
                resume_doc = self._nlp(resume_text[:5000])  # Limit for performance
                jd_doc = self._nlp(jd_text[:3000])
                if resume_doc.has_vector and jd_doc.has_vector:
                    semantic_score = resume_doc.similarity(jd_doc) * 100
            except Exception:
                pass

        # Blend: 60% TF-IDF (precise matching) + 40% semantic (meaning matching)
        if semantic_score > 0:
            blended = tfidf_score * 0.6 + semantic_score * 0.4
        else:
            blended = tfidf_score

        return min(100, max(0, round(blended)))
