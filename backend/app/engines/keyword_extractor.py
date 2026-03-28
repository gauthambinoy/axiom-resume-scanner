import re
from collections import Counter
from dataclasses import dataclass, field

from app.engines.constants import (
    ALL_SKILLS,
    SKILL_CATEGORIES,
    SOFT_SKILLS,
    CERTIFICATION_PATTERNS,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class KeywordExtractionResult:
    technical_skills: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    tools_and_platforms: list[str] = field(default_factory=list)
    action_verbs: list[str] = field(default_factory=list)
    domain_terms: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    all_keywords: list[str] = field(default_factory=list)
    keyword_frequency: dict[str, int] = field(default_factory=dict)
    priority_keywords: list[str] = field(default_factory=list)
    is_empty: bool = False
    warning: str = ""


class KeywordExtractor:
    def __init__(self) -> None:
        self._nlp = None
        self._spacy_available = False
        try:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
            self._spacy_available = True
        except (OSError, ImportError):
            logger.warning("spaCy model not available, falling back to regex extraction")

    def extract(self, jd_text: str) -> KeywordExtractionResult:
        try:
            if not jd_text or not jd_text.strip():
                return KeywordExtractionResult(is_empty=True, warning="Empty input")

            jd_text = jd_text.strip()
            if len(jd_text) < 50:
                result = self._extract_regex(jd_text)
                result.warning = "Input text is very short, results may be incomplete"
                return result

            if self._spacy_available and self._nlp is not None:
                return self._extract_with_spacy(jd_text)
            return self._extract_regex(jd_text)
        except Exception as e:
            logger.error("Keyword extraction failed", error=str(e))
            return self._extract_regex(jd_text)

    def _extract_with_spacy(self, text: str) -> KeywordExtractionResult:
        doc = self._nlp(text)  # type: ignore[misc]
        text_lower = text.lower()

        # Technical skills
        technical_skills = self._match_skills(text_lower)

        # Tools and platforms (cloud + devops + tools categories)
        tools_cats = {"cloud", "devops", "tools"}
        tools_and_platforms = []
        for cat, skills in SKILL_CATEGORIES.items():
            if cat in tools_cats:
                for skill in skills:
                    if skill in text_lower:
                        tools_and_platforms.append(skill)

        # Soft skills
        soft_skills = [s for s in SOFT_SKILLS if s in text_lower]

        # Action verbs via POS tagging
        verb_tags = {"VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}
        action_verbs_counter: Counter[str] = Counter()
        for token in doc:
            if token.tag_ in verb_tags and len(token.text) > 2 and token.text.lower() not in {
                "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                "do", "does", "did", "will", "would", "could", "should", "may", "might",
                "shall", "can",
            }:
                action_verbs_counter[token.lemma_.lower()] += 1
        action_verbs = [v for v, _ in action_verbs_counter.most_common(20)]

        # Named entities
        domain_terms: list[str] = []
        for ent in doc.ents:
            if ent.label_ in {"ORG", "PRODUCT", "GPE"} and len(ent.text) > 1:
                term = ent.text.strip().lower()
                if term not in domain_terms:
                    domain_terms.append(term)

        # Domain-specific nouns appearing 2+ times
        noun_counter: Counter[str] = Counter()
        for token in doc:
            if token.pos_ == "NOUN" and len(token.text) > 2 and not token.is_stop:
                noun_counter[token.lemma_.lower()] += 1
        for noun, count in noun_counter.items():
            if count >= 2 and noun not in domain_terms:
                domain_terms.append(noun)

        # Certifications
        certifications = self._extract_certifications(text)

        # Build combined results
        return self._build_result(
            technical_skills, soft_skills, tools_and_platforms,
            action_verbs, domain_terms, certifications, text_lower,
        )

    def _extract_regex(self, text: str) -> KeywordExtractionResult:
        text_lower = text.lower()

        technical_skills = self._match_skills(text_lower)

        tools_cats = {"cloud", "devops", "tools"}
        tools_and_platforms = []
        for cat, skills in SKILL_CATEGORIES.items():
            if cat in tools_cats:
                for skill in skills:
                    if skill in text_lower:
                        tools_and_platforms.append(skill)

        soft_skills = [s for s in SOFT_SKILLS if s in text_lower]

        # Simple verb extraction via common action verbs
        common_verbs = [
            "build", "develop", "design", "manage", "lead", "implement", "create",
            "analyze", "optimize", "deploy", "configure", "monitor", "maintain",
            "collaborate", "communicate", "deliver", "test", "debug", "architect",
            "scale", "automate", "integrate", "write", "review", "mentor",
        ]
        action_verbs = [v for v in common_verbs if re.search(rf"\b{v}\w*\b", text_lower)]

        # Domain terms: capitalized multi-word phrases
        domain_terms: list[str] = []
        for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text):
            term = match.group(1).lower()
            if term not in domain_terms and len(term) > 3:
                domain_terms.append(term)

        certifications = self._extract_certifications(text)

        return self._build_result(
            technical_skills, soft_skills, tools_and_platforms,
            action_verbs, domain_terms, certifications, text_lower,
        )

    def _match_skills(self, text_lower: str) -> list[str]:
        found: list[str] = []
        for skill in ALL_SKILLS:
            pattern = rf"\b{re.escape(skill)}\b"
            try:
                if re.search(pattern, text_lower):
                    found.append(skill)
            except re.error:
                if skill in text_lower:
                    found.append(skill)
        return found

    def _extract_certifications(self, text: str) -> list[str]:
        certs: list[str] = []
        for pattern in CERTIFICATION_PATTERNS:
            try:
                matches = re.findall(pattern, text)
                for m in matches:
                    cert = m if isinstance(m, str) else m[0] if m else ""
                    cert = cert.strip()
                    if cert and cert.lower() not in [c.lower() for c in certs]:
                        certs.append(cert)
            except re.error:
                continue
        return certs

    def _build_result(
        self,
        technical_skills: list[str],
        soft_skills: list[str],
        tools_and_platforms: list[str],
        action_verbs: list[str],
        domain_terms: list[str],
        certifications: list[str],
        text_lower: str,
    ) -> KeywordExtractionResult:
        # Deduplicate
        all_set: set[str] = set()
        all_keywords: list[str] = []
        for kw_list in [technical_skills, soft_skills, tools_and_platforms, action_verbs, domain_terms, certifications]:
            for kw in kw_list:
                kw_norm = kw.lower().strip()
                if kw_norm not in all_set:
                    all_set.add(kw_norm)
                    all_keywords.append(kw_norm)

        # Frequency counts
        keyword_frequency: dict[str, int] = {}
        for kw in all_keywords:
            try:
                count = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower))
            except re.error:
                count = text_lower.count(kw)
            keyword_frequency[kw] = max(count, 1)

        # Priority = top 20 by frequency
        sorted_kw = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)
        priority_keywords = [kw for kw, _ in sorted_kw[:20]]

        return KeywordExtractionResult(
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            tools_and_platforms=tools_and_platforms,
            action_verbs=action_verbs,
            domain_terms=domain_terms,
            certifications=certifications,
            all_keywords=all_keywords,
            keyword_frequency=keyword_frequency,
            priority_keywords=priority_keywords,
        )
