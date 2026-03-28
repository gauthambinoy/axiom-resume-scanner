import re
import statistics
from dataclasses import dataclass, field

from app.engines.constants import (
    BANNED_FIRST_WORDS,
    BANNED_PHRASES,
    BANNED_EXTENDED_WORDS,
    AI_STRUCTURE_PATTERNS,
    ROUND_NUMBERS,
    TRANSITIONAL_OPENERS,
    OPENER_SYNONYM_GROUPS,
)
from app.engines.section_parser import SectionParseResult, BulletPoint
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_SIGNAL_SCORE = 100.0 / 12  # ~8.33


@dataclass
class DetectionSignal:
    name: str
    score: float
    max_score: float = MAX_SIGNAL_SCORE
    details: str = ""
    flagged_items: list[str] = field(default_factory=list)


@dataclass
class BulletAnalysis:
    text: str
    word_count: int
    structure_type: str
    first_word: str
    has_banned_phrase: bool
    banned_phrases_found: list[str] = field(default_factory=list)
    ends_with_metric: bool = False
    flags: list[str] = field(default_factory=list)
    ai_risk: str = "clean"


@dataclass
class SummaryAnalysis:
    adjective_count: int = 0
    adjectives_found: list[str] = field(default_factory=list)
    starts_with_adjective: bool = False
    word_count: int = 0
    has_years_experience: bool = False
    has_seniority_label: bool = False


@dataclass
class AIDetectionResult:
    overall_score: float = 0.0
    risk_level: str = "LOW"
    signals: list[DetectionSignal] = field(default_factory=list)
    per_bullet_analysis: list[BulletAnalysis] = field(default_factory=list)
    summary_analysis: SummaryAnalysis = field(default_factory=SummaryAnalysis)
    top_issues: list[str] = field(default_factory=list)


class AIDetectionEngine:
    def __init__(self) -> None:
        self._nlp = None
        try:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        except (OSError, ImportError):
            pass

    def analyze(
        self,
        resume_text: str,
        sections: SectionParseResult,
        bullets: list[BulletPoint],
    ) -> AIDetectionResult:
        try:
            result = AIDetectionResult()
            if not bullets:
                result.risk_level = "LOW"
                return result

            signals: list[DetectionSignal] = []

            signals.append(self._signal_sentence_length_variance(bullets))
            signals.append(self._signal_consecutive_length(bullets))
            signals.append(self._signal_opening_repetition(bullets))
            signals.append(self._signal_banned_phrase_density(resume_text))
            signals.append(self._signal_banned_word_density(resume_text))
            signals.append(self._signal_structure_uniformity(bullets))
            signals.append(self._signal_round_numbers(bullets))
            signals.append(self._signal_ai_patterns(resume_text))
            signals.append(self._signal_metric_saturation(bullets))
            signals.append(self._signal_adjective_density(sections.summary_text))
            signals.append(self._signal_transitional_overuse(bullets))
            signals.append(self._signal_vocabulary_predictability(bullets))

            result.signals = signals
            result.overall_score = round(sum(s.score for s in signals), 2)
            result.overall_score = min(100.0, max(0.0, result.overall_score))

            # Risk level
            if result.overall_score <= 25:
                result.risk_level = "LOW"
            elif result.overall_score <= 50:
                result.risk_level = "MODERATE"
            elif result.overall_score <= 75:
                result.risk_level = "HIGH"
            else:
                result.risk_level = "CRITICAL"

            # Per-bullet analysis
            result.per_bullet_analysis = self._analyze_bullets(bullets, resume_text)

            # Summary analysis
            result.summary_analysis = self._analyze_summary(sections.summary_text)

            # Top issues
            sorted_signals = sorted(signals, key=lambda s: s.score, reverse=True)
            result.top_issues = [
                f"{s.name}: {s.details}" for s in sorted_signals[:5] if s.score > 0
            ]

            return result
        except Exception as e:
            logger.error("AI detection failed", error=str(e))
            return AIDetectionResult()

    def _signal_sentence_length_variance(self, bullets: list[BulletPoint]) -> DetectionSignal:
        name = "Sentence Length Variance"
        word_counts = [b.word_count for b in bullets]
        if len(word_counts) < 2:
            return DetectionSignal(name=name, score=0, details="Not enough bullets to analyze")

        std_dev = statistics.stdev(word_counts)
        flagged: list[str] = []

        # Flag consecutive pairs with <3 word difference
        for i in range(len(word_counts) - 1):
            if abs(word_counts[i] - word_counts[i + 1]) < 3:
                flagged.append(f"Bullets {i+1} and {i+2} differ by <3 words ({word_counts[i]} vs {word_counts[i+1]})")

        if std_dev < 2.5:
            score = MAX_SIGNAL_SCORE
            details = f"Very uniform bullet lengths (std dev: {std_dev:.1f}). Highly suspicious."
        elif std_dev < 4.0:
            score = 6.5
            details = f"Fairly uniform bullet lengths (std dev: {std_dev:.1f})."
        elif std_dev < 6.0:
            score = 4.0
            details = f"Moderate length variation (std dev: {std_dev:.1f})."
        elif std_dev < 8.0:
            score = 2.0
            details = f"Good length variation (std dev: {std_dev:.1f})."
        else:
            score = 0
            details = f"Natural length variation (std dev: {std_dev:.1f})."

        return DetectionSignal(name=name, score=score, details=details, flagged_items=flagged)

    def _signal_consecutive_length(self, bullets: list[BulletPoint]) -> DetectionSignal:
        name = "Consecutive Length Similarity"
        if len(bullets) < 2:
            return DetectionSignal(name=name, score=0, details="Not enough bullets")

        total_pairs = len(bullets) - 1
        similar_pairs = 0
        flagged: list[str] = []

        for i in range(total_pairs):
            diff = abs(bullets[i].word_count - bullets[i + 1].word_count)
            if diff < 5:
                similar_pairs += 1
                flagged.append(f"Bullets {i+1}-{i+2}: {bullets[i].word_count} vs {bullets[i+1].word_count} words")

        pct = (similar_pairs / total_pairs) * 100

        if pct >= 60:
            score = MAX_SIGNAL_SCORE
        elif pct >= 40:
            score = 5.5
        elif pct >= 20:
            score = 3.0
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{similar_pairs}/{total_pairs} consecutive pairs have similar length ({pct:.0f}%)",
            flagged_items=flagged,
        )

    def _signal_opening_repetition(self, bullets: list[BulletPoint]) -> DetectionSignal:
        name = "Opening Word Repetition"
        from collections import Counter

        first_words = [b.first_word for b in bullets if b.first_word]
        word_counts = Counter(first_words)
        flagged: list[str] = []

        max_count = max(word_counts.values()) if word_counts else 0

        # Check synonym groups
        synonym_score = 0
        for group in OPENER_SYNONYM_GROUPS:
            found_in_group = [w for w in first_words if w in group]
            if len(found_in_group) >= 2:
                synonym_score += 1
                flagged.append(f"Synonym group: {', '.join(set(found_in_group))}")

        for word, count in word_counts.items():
            if count >= 2:
                indices = [i + 1 for i, b in enumerate(bullets) if b.first_word == word]
                flagged.append(f"'{word}' opens bullets: {indices}")

        if max_count >= 4 or synonym_score >= 3:
            score = MAX_SIGNAL_SCORE
        elif max_count >= 3 or synonym_score >= 2:
            score = 6.0
        elif max_count >= 2 or synonym_score >= 1:
            score = 3.0
        else:
            score = 0

        details = f"Max repetition: {max_count}x, synonym groups: {synonym_score}"
        return DetectionSignal(name=name, score=score, details=details, flagged_items=flagged)

    def _signal_banned_phrase_density(self, text: str) -> DetectionSignal:
        name = "Banned Phrase Density"
        text_lower = text.lower()
        found: list[str] = []

        for phrase in BANNED_PHRASES:
            if phrase in text_lower:
                found.append(phrase)

        count = len(found)
        if count >= 8:
            score = MAX_SIGNAL_SCORE
        elif count >= 5:
            score = 6.0
        elif count >= 3:
            score = 4.0
        elif count >= 1:
            score = 2.0
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{count} banned phrases found",
            flagged_items=found,
        )

    def _signal_banned_word_density(self, text: str) -> DetectionSignal:
        name = "Banned Word Density"
        text_lower = text.lower()
        found: list[str] = []

        for word in BANNED_EXTENDED_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", text_lower):
                found.append(word)

        count = len(found)
        if count >= 6:
            score = MAX_SIGNAL_SCORE
        elif count >= 4:
            score = 5.5
        elif count >= 2:
            score = 3.0
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{count} AI-flagged words found",
            flagged_items=found,
        )

    def _signal_structure_uniformity(self, bullets: list[BulletPoint]) -> DetectionSignal:
        name = "Structure Uniformity"
        if not bullets:
            return DetectionSignal(name=name, score=0, details="No bullets")

        types = [self._classify_structure(b) for b in bullets]
        from collections import Counter
        type_counts = Counter(types)
        dominant_type, dominant_count = type_counts.most_common(1)[0]
        pct = (dominant_count / len(bullets)) * 100

        if pct >= 75:
            score = MAX_SIGNAL_SCORE
        elif pct >= 60:
            score = 5.5
        elif pct >= 45:
            score = 3.0
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{pct:.0f}% of bullets use '{dominant_type}' structure",
            flagged_items=[f"Types: {dict(type_counts)}"],
        )

    def _classify_structure(self, bullet: BulletPoint) -> str:
        text = bullet.text
        first = bullet.first_word
        words = text.split()

        if not words:
            return "TYPE_SHORT_DECLARATIVE"

        # Check first person
        if any(w.lower() == "i" for w in words[:5]):
            return "TYPE_FIRST_PERSON"

        # Gerund
        if first.endswith("ing") and len(first) > 4:
            return "TYPE_GERUND"

        # Context first
        if first in {"under", "for", "with", "during", "within", "across", "through", "after", "before"}:
            return "TYPE_CONTEXT_FIRST"

        # Outcome first (starts with number)
        if re.match(r"\d", first):
            return "TYPE_OUTCOME_FIRST"

        # Object first
        if first in {"the", "a", "an", "this", "that", "our", "their", "my"}:
            return "TYPE_OBJECT_FIRST"

        # Narrative
        narrative_markers = {"started", "turned", "began", "what", "originally"}
        if first in narrative_markers:
            return "TYPE_NARRATIVE"

        # Short declarative
        if bullet.word_count < 15:
            return "TYPE_SHORT_DECLARATIVE"

        # Default: verb first (most common AI pattern)
        return "TYPE_VERB_FIRST"

    def _signal_round_numbers(self, bullets: list[BulletPoint]) -> DetectionSignal:
        name = "Round Number Usage"
        flagged: list[str] = []

        for i, b in enumerate(bullets):
            for match in re.finditer(r"(\d+(?:\.\d+)?)\s*%", b.text):
                try:
                    val = float(match.group(1))
                    if val in ROUND_NUMBERS:
                        flagged.append(f"Bullet {i+1}: '{match.group(0)}'")
                except ValueError:
                    continue
            # Also check multipliers like "3x", "5x"
            for match in re.finditer(r"\b(\d+)[xX]\b", b.text):
                try:
                    val = int(match.group(1))
                    if val in {2, 3, 4, 5, 10}:
                        flagged.append(f"Bullet {i+1}: '{match.group(0)}'")
                except ValueError:
                    continue

        count = len(flagged)
        if count >= 4:
            score = MAX_SIGNAL_SCORE
        elif count >= 3:
            score = 6.0
        elif count >= 2:
            score = 4.0
        elif count >= 1:
            score = 2.0
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{count} round/suspicious numbers found",
            flagged_items=flagged,
        )

    def _signal_ai_patterns(self, text: str) -> DetectionSignal:
        name = "AI Sentence Patterns"
        flagged: list[str] = []

        for pattern in AI_STRUCTURE_PATTERNS:
            try:
                matches = re.findall(pattern, text, re.MULTILINE)
                for m in matches:
                    match_text = m if isinstance(m, str) else m[0] if m else ""
                    if match_text:
                        flagged.append(f"Pattern match: '{match_text[:60]}...'")
            except re.error:
                continue

        count = len(flagged)
        if count >= 5:
            score = MAX_SIGNAL_SCORE
        elif count >= 3:
            score = 5.5
        elif count >= 1:
            score = 3.0
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{count} AI-typical sentence patterns found",
            flagged_items=flagged,
        )

    def _signal_metric_saturation(self, bullets: list[BulletPoint]) -> DetectionSignal:
        name = "Metric Saturation"
        if not bullets:
            return DetectionSignal(name=name, score=0, details="No bullets")

        metric_end_count = sum(1 for b in bullets if b.ends_with_metric)
        pct = (metric_end_count / len(bullets)) * 100

        if pct >= 80:
            score = MAX_SIGNAL_SCORE
        elif pct >= 60:
            score = 5.5
        elif pct >= 40:
            score = 3.0
        elif pct >= 20:
            score = 1.5
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{metric_end_count}/{len(bullets)} bullets ({pct:.0f}%) end with metrics",
            flagged_items=[],
        )

    def _signal_adjective_density(self, summary_text: str) -> DetectionSignal:
        name = "Summary Adjective Density"
        if not summary_text or not summary_text.strip():
            return DetectionSignal(name=name, score=0, details="No summary section found")

        adjectives: list[str] = []

        if self._nlp:
            doc = self._nlp(summary_text)
            for token in doc:
                if token.tag_ in {"JJ", "JJR", "JJS"}:
                    adjectives.append(token.text.lower())
        else:
            # Fallback: common resume adjectives
            common_adj = {
                "experienced", "skilled", "proficient", "passionate", "dedicated",
                "innovative", "dynamic", "results-driven", "detail-oriented", "strategic",
                "creative", "analytical", "collaborative", "motivated", "proven",
                "strong", "excellent", "comprehensive", "effective", "successful",
            }
            words = summary_text.lower().split()
            adjectives = [w.strip(".,;:") for w in words if w.strip(".,;:") in common_adj]

        count = len(adjectives)
        if count >= 6:
            score = MAX_SIGNAL_SCORE
        elif count >= 4:
            score = 5.5
        elif count >= 2:
            score = 2.5
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{count} adjectives in summary",
            flagged_items=list(set(adjectives)),
        )

    def _signal_transitional_overuse(self, bullets: list[BulletPoint]) -> DetectionSignal:
        name = "Transitional Word Overuse"
        flagged: list[str] = []

        for i, b in enumerate(bullets):
            if b.first_word in TRANSITIONAL_OPENERS:
                flagged.append(f"Bullet {i+1} starts with '{b.first_word}'")

        count = len(flagged)
        if count >= 4:
            score = MAX_SIGNAL_SCORE
        elif count >= 2:
            score = 4.0
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{count} bullets start with transitional words",
            flagged_items=flagged,
        )

    def _signal_vocabulary_predictability(self, bullets: list[BulletPoint]) -> DetectionSignal:
        name = "Vocabulary Predictability"
        if not bullets:
            return DetectionSignal(name=name, score=0, details="No bullets")

        # Pattern: [Past tense verb] + [object] + [prep phrase] + [metric]
        ai_pattern = re.compile(
            r"^[A-Z][a-z]+ed\s+.+(?:using|with|by|through|via|leveraging)\s+.+\d",
            re.IGNORECASE,
        )

        match_count = 0
        flagged: list[str] = []
        for i, b in enumerate(bullets):
            if ai_pattern.match(b.text):
                match_count += 1
                flagged.append(f"Bullet {i+1}: follows Verb+Object+Prep+Metric pattern")

        pct = (match_count / len(bullets)) * 100

        if pct >= 70:
            score = MAX_SIGNAL_SCORE
        elif pct >= 50:
            score = 5.5
        elif pct >= 30:
            score = 3.0
        else:
            score = 0

        return DetectionSignal(
            name=name, score=score,
            details=f"{match_count}/{len(bullets)} ({pct:.0f}%) match predictable AI pattern",
            flagged_items=flagged,
        )

    def _analyze_bullets(self, bullets: list[BulletPoint], full_text: str) -> list[BulletAnalysis]:
        analyses: list[BulletAnalysis] = []
        text_lower = full_text.lower()

        for b in bullets:
            struct_type = self._classify_structure(b)
            banned_found: list[str] = []
            for phrase in BANNED_PHRASES:
                if phrase in b.text.lower():
                    banned_found.append(phrase)

            flags: list[str] = []
            if b.first_word in BANNED_FIRST_WORDS:
                flags.append(f"Banned first word: '{b.first_word}'")
            if banned_found:
                flags.append(f"Banned phrases: {', '.join(banned_found)}")
            if b.ends_with_metric:
                flags.append("Ends with metric")

            for word in BANNED_EXTENDED_WORDS:
                if re.search(rf"\b{re.escape(word)}\b", b.text.lower()):
                    flags.append(f"AI-flagged word: '{word}'")

            flag_count = len(flags)
            if flag_count >= 3:
                risk = "flagged"
            elif flag_count >= 1:
                risk = "suspicious"
            else:
                risk = "clean"

            analyses.append(BulletAnalysis(
                text=b.text,
                word_count=b.word_count,
                structure_type=struct_type,
                first_word=b.first_word,
                has_banned_phrase=len(banned_found) > 0,
                banned_phrases_found=banned_found,
                ends_with_metric=b.ends_with_metric,
                flags=flags,
                ai_risk=risk,
            ))

        return analyses

    def _analyze_summary(self, summary_text: str) -> SummaryAnalysis:
        analysis = SummaryAnalysis()
        if not summary_text:
            return analysis

        analysis.word_count = len(summary_text.split())

        if self._nlp:
            doc = self._nlp(summary_text)
            for token in doc:
                if token.tag_ in {"JJ", "JJR", "JJS"}:
                    analysis.adjectives_found.append(token.text.lower())
            analysis.adjective_count = len(analysis.adjectives_found)

            first_token = doc[0] if len(doc) > 0 else None
            if first_token and first_token.tag_ in {"JJ", "JJR", "JJS"}:
                analysis.starts_with_adjective = True
        else:
            common_adj = {
                "experienced", "skilled", "proficient", "passionate", "dedicated",
                "innovative", "dynamic", "strategic", "creative", "analytical",
                "motivated", "proven", "strong", "excellent", "effective",
            }
            words = summary_text.lower().split()
            analysis.adjectives_found = [w.strip(".,;:") for w in words if w.strip(".,;:") in common_adj]
            analysis.adjective_count = len(analysis.adjectives_found)
            if words and words[0].strip(".,;:") in common_adj:
                analysis.starts_with_adjective = True

        analysis.has_years_experience = bool(re.search(r"\d+\+?\s*years?\s+(?:of\s+)?experience", summary_text, re.I))
        seniority = {"senior", "lead", "principal", "staff", "junior", "mid-level", "entry-level"}
        analysis.has_seniority_label = any(s in summary_text.lower() for s in seniority)

        return analysis
