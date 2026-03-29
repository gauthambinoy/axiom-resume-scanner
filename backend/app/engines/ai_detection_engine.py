import math
import os
import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
import httpx

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

NUM_SIGNALS = 19  # 12 original + 5 advanced + 2 ML-based
MAX_SIGNAL_SCORE = 100.0 / NUM_SIGNALS  # ~5.26


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
class HeatmapItem:
    text: str
    risk: float  # 0.0 to 1.0
    flags: list[str] = field(default_factory=list)
    color: str = "green"  # green, yellow, orange, red


@dataclass
class AIDetectionResult:
    overall_score: float = 0.0
    risk_level: str = "LOW"
    signals: list[DetectionSignal] = field(default_factory=list)
    per_bullet_analysis: list[BulletAnalysis] = field(default_factory=list)
    summary_analysis: SummaryAnalysis = field(default_factory=SummaryAnalysis)
    top_issues: list[str] = field(default_factory=list)
    heatmap: list[HeatmapItem] = field(default_factory=list)


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

            # Original 12 signals
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
            # 5 new advanced signals
            signals.append(self._signal_entropy_analysis(bullets))
            signals.append(self._signal_ngram_repetition(resume_text))
            signals.append(self._signal_burstiness(bullets))
            signals.append(self._signal_punctuation_patterns(bullets))
            signals.append(self._signal_passive_voice_density(resume_text))
            # 2 ML-based signals
            signals.append(self._signal_ml_classifier(resume_text))
            signals.append(self._signal_perplexity_estimate(resume_text))

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

            # Heatmap
            result.heatmap = self.generate_heatmap(resume_text, result.per_bullet_analysis)

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

    # ── New advanced signals ──────────────────────────────────────────

    def _signal_entropy_analysis(self, bullets: list[BulletPoint]) -> DetectionSignal:
        """Measure word-level entropy (Shannon). AI text tends toward lower entropy
        because it uses a narrower, more predictable vocabulary."""
        name = "Vocabulary Entropy"
        if len(bullets) < 3:
            return DetectionSignal(name=name, score=0, details="Not enough bullets")

        all_words = []
        for b in bullets:
            all_words.extend(w.lower().strip(".,;:!?()") for w in b.text.split() if len(w) > 2)

        if len(all_words) < 20:
            return DetectionSignal(name=name, score=0, details="Not enough words")

        word_counts = Counter(all_words)
        total = len(all_words)
        entropy = -sum((c / total) * math.log2(c / total) for c in word_counts.values())

        # Normalize: max entropy for N unique words = log2(N)
        max_entropy = math.log2(len(word_counts)) if len(word_counts) > 1 else 1
        normalized = entropy / max_entropy  # 0-1, lower = more repetitive/AI-like

        if normalized < 0.70:
            score = MAX_SIGNAL_SCORE
            details = f"Very low vocabulary diversity (entropy ratio: {normalized:.2f}). AI-typical."
        elif normalized < 0.78:
            score = MAX_SIGNAL_SCORE * 0.65
            details = f"Below-average vocabulary diversity (entropy ratio: {normalized:.2f})."
        elif normalized < 0.85:
            score = MAX_SIGNAL_SCORE * 0.35
            details = f"Moderate vocabulary diversity (entropy ratio: {normalized:.2f})."
        else:
            score = 0
            details = f"Natural vocabulary diversity (entropy ratio: {normalized:.2f})."

        return DetectionSignal(name=name, score=round(score, 2), details=details)

    def _signal_ngram_repetition(self, text: str) -> DetectionSignal:
        """Detect repeated 3-grams and 4-grams. AI text reuses phrasal templates
        at higher rates than human writing."""
        name = "N-gram Repetition"
        words = [w.lower().strip(".,;:!?()") for w in text.split() if w.strip()]

        if len(words) < 30:
            return DetectionSignal(name=name, score=0, details="Not enough text")

        flagged: list[str] = []

        # Check 3-grams
        trigrams = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]
        tri_counts = Counter(trigrams)
        repeated_tri = {ng: c for ng, c in tri_counts.items() if c >= 3}

        # Check 4-grams
        fourgrams = [" ".join(words[i:i+4]) for i in range(len(words) - 3)]
        four_counts = Counter(fourgrams)
        repeated_four = {ng: c for ng, c in four_counts.items() if c >= 2}

        # Filter out trivial n-grams (stopword-only)
        stopwords = {"the", "a", "an", "in", "of", "to", "and", "for", "with", "on", "at", "by", "is", "was", "are", "were"}
        for ng, count in repeated_tri.items():
            if not all(w in stopwords for w in ng.split()):
                flagged.append(f"3-gram '{ng}' appears {count}x")
        for ng, count in repeated_four.items():
            if not all(w in stopwords for w in ng.split()):
                flagged.append(f"4-gram '{ng}' appears {count}x")

        count = len(flagged)
        if count >= 8:
            score = MAX_SIGNAL_SCORE
        elif count >= 5:
            score = MAX_SIGNAL_SCORE * 0.7
        elif count >= 3:
            score = MAX_SIGNAL_SCORE * 0.4
        elif count >= 1:
            score = MAX_SIGNAL_SCORE * 0.2
        else:
            score = 0

        return DetectionSignal(
            name=name, score=round(score, 2),
            details=f"{count} repeated n-gram patterns found",
            flagged_items=flagged[:10],
        )

    def _signal_burstiness(self, bullets: list[BulletPoint]) -> DetectionSignal:
        """Measure sentence-length burstiness. Human writing is 'bursty' — clusters of
        short and long sentences. AI writing is uniformly distributed."""
        name = "Burstiness"
        if len(bullets) < 5:
            return DetectionSignal(name=name, score=0, details="Not enough bullets")

        lengths = [b.word_count for b in bullets]
        mean_len = statistics.mean(lengths)

        # Burstiness = (std - mean) / (std + mean). Range: -1 to 1.
        # Human text: positive burstiness. AI text: near 0 or negative.
        std_len = statistics.stdev(lengths)
        if (std_len + mean_len) == 0:
            burstiness = 0.0
        else:
            burstiness = (std_len - mean_len) / (std_len + mean_len)

        # Also check for runs: consecutive bullets in same length bucket
        short_thresh = mean_len * 0.7
        long_thresh = mean_len * 1.3
        buckets = []
        for l in lengths:
            if l < short_thresh:
                buckets.append("short")
            elif l > long_thresh:
                buckets.append("long")
            else:
                buckets.append("medium")

        # Count run changes (human writing has more varied runs)
        changes = sum(1 for i in range(1, len(buckets)) if buckets[i] != buckets[i-1])
        change_rate = changes / max(len(buckets) - 1, 1)

        # Low burstiness AND low change rate = AI-like
        if burstiness > -0.3 and change_rate < 0.35:
            score = MAX_SIGNAL_SCORE
            details = f"Very low burstiness ({burstiness:.2f}) with monotone rhythm ({change_rate:.0%} changes). AI-typical."
        elif burstiness > -0.2 and change_rate < 0.50:
            score = MAX_SIGNAL_SCORE * 0.6
            details = f"Low burstiness ({burstiness:.2f}), limited rhythm variation ({change_rate:.0%} changes)."
        elif change_rate < 0.40:
            score = MAX_SIGNAL_SCORE * 0.3
            details = f"Moderate burstiness ({burstiness:.2f}), some rhythm ({change_rate:.0%} changes)."
        else:
            score = 0
            details = f"Natural burstiness ({burstiness:.2f}) with varied rhythm ({change_rate:.0%} changes)."

        return DetectionSignal(name=name, score=round(score, 2), details=details)

    def _signal_punctuation_patterns(self, bullets: list[BulletPoint]) -> DetectionSignal:
        """AI text has very uniform punctuation usage — few semicolons, parentheticals,
        dashes, or em-dashes. Human writers use more varied punctuation."""
        name = "Punctuation Uniformity"
        if len(bullets) < 3:
            return DetectionSignal(name=name, score=0, details="Not enough bullets")

        # Count punctuation variety per bullet
        varied_punct = set("();:—–-/")
        total_bullets = len(bullets)
        bullets_with_varied_punct = 0
        all_text = " ".join(b.text for b in bullets)

        for b in bullets:
            if any(c in b.text for c in varied_punct):
                bullets_with_varied_punct += 1

        # Count specific patterns
        has_parens = bool(re.search(r"\([^)]+\)", all_text))
        has_semicolons = ";" in all_text
        has_dashes = bool(re.search(r"\s[—–-]\s", all_text))
        has_colons_inline = bool(re.search(r"\w:\s\w", all_text))

        variety_score = sum([has_parens, has_semicolons, has_dashes, has_colons_inline])
        varied_pct = bullets_with_varied_punct / total_bullets

        # Low punctuation variety = AI-like
        if variety_score == 0 and varied_pct < 0.2:
            score = MAX_SIGNAL_SCORE
            details = "No punctuation variety at all — every bullet uses only commas and periods. AI-typical."
        elif variety_score <= 1 and varied_pct < 0.3:
            score = MAX_SIGNAL_SCORE * 0.65
            details = f"Very limited punctuation variety (score: {variety_score}/4)."
        elif variety_score <= 2:
            score = MAX_SIGNAL_SCORE * 0.3
            details = f"Moderate punctuation variety (score: {variety_score}/4)."
        else:
            score = 0
            details = f"Good punctuation variety (score: {variety_score}/4). Natural writing."

        return DetectionSignal(name=name, score=round(score, 2), details=details)

    def _signal_passive_voice_density(self, text: str) -> DetectionSignal:
        """AI resumes heavily favor active voice ('Developed X'). Paradoxically,
        zero passive voice is a signal — human writers occasionally use it naturally."""
        name = "Voice Pattern Analysis"
        if not text or len(text.split()) < 30:
            return DetectionSignal(name=name, score=0, details="Not enough text")

        # Detect passive constructions
        passive_patterns = [
            r"(?i)\b(?:was|were|been|being|is|are)\s+\w+ed\b",
            r"(?i)\b(?:was|were|been|being|is|are)\s+\w+en\b",
            r"(?i)\b(?:got|get|gets)\s+\w+ed\b",
        ]

        passive_count = 0
        for pattern in passive_patterns:
            passive_count += len(re.findall(pattern, text))

        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        total_sentences = len(sentences)

        if total_sentences == 0:
            return DetectionSignal(name=name, score=0, details="No sentences found")

        passive_ratio = passive_count / total_sentences

        # ALL active (ratio ~0) is actually suspicious for AI
        # Some passive (0.05-0.25) is natural
        # Too much passive (>0.4) is bad writing but not AI-specific
        if passive_ratio < 0.02 and total_sentences > 5:
            score = MAX_SIGNAL_SCORE * 0.7
            details = f"100% active voice across {total_sentences} sentences. AI-typical (humans occasionally use passive)."
        elif passive_ratio < 0.05:
            score = MAX_SIGNAL_SCORE * 0.4
            details = f"Almost exclusively active voice ({passive_ratio:.0%} passive). Slightly suspicious."
        elif passive_ratio <= 0.25:
            score = 0
            details = f"Natural mix of active/passive voice ({passive_ratio:.0%} passive)."
        else:
            score = MAX_SIGNAL_SCORE * 0.3
            details = f"High passive voice usage ({passive_ratio:.0%}). Unusual but not AI-typical."

        return DetectionSignal(name=name, score=round(score, 2), details=details)

    # ── ML-based signals ──────────────────────────────────────────────

    # Class-level cache for ML classifier results keyed by text hash
    _ml_cache: dict[int, DetectionSignal] = {}

    def _signal_ml_classifier(self, text: str) -> DetectionSignal:
        """Call HuggingFace's RoBERTa-based OpenAI detector via Inference API.
        Returns a score based on the model's 'Fake' (AI-generated) probability."""
        name = "ML Classifier (RoBERTa)"

        if not text or len(text.strip()) < 50:
            return DetectionSignal(name=name, score=0, details="Not enough text for ML classification")

        # Check cache
        text_hash = hash(text)
        if text_hash in self._ml_cache:
            return self._ml_cache[text_hash]

        # Truncate to ~2000 chars to respect model's 512-token limit
        truncated = text[:2000]

        api_url = "https://api-inference.huggingface.co/models/openai-community/roberta-base-openai-detector"
        headers: dict[str, str] = {}
        hf_key = os.environ.get("HUGGINGFACE_API_KEY")
        if hf_key:
            headers["Authorization"] = f"Bearer {hf_key}"

        try:
            response = httpx.post(
                api_url,
                json={"inputs": truncated},
                headers=headers,
                timeout=5.0,
            )
            response.raise_for_status()
            result = response.json()

            # Response format: [[{"label": "Fake", "score": 0.8}, {"label": "Real", "score": 0.2}]]
            # or [{"label": "Fake", "score": 0.8}, ...]
            labels = result[0] if isinstance(result, list) and result else result
            if isinstance(labels, list):
                label_scores = {item["label"]: item["score"] for item in labels}
            else:
                signal = DetectionSignal(
                    name=name, score=0,
                    details="ML classifier returned unexpected format",
                )
                self._ml_cache[text_hash] = signal
                return signal

            fake_prob = label_scores.get("Fake", label_scores.get("LABEL_0", 0.0))
            real_prob = label_scores.get("Real", label_scores.get("LABEL_1", 0.0))

            if fake_prob > 0.85:
                score = MAX_SIGNAL_SCORE
                details = f"ML classifier: {fake_prob:.0%} probability AI-generated"
            elif fake_prob > 0.7:
                score = MAX_SIGNAL_SCORE * 0.7
                details = f"ML classifier: {fake_prob:.0%} probability AI-generated"
            elif fake_prob > 0.6:
                score = MAX_SIGNAL_SCORE * 0.4
                details = f"ML classifier: {fake_prob:.0%} probability AI-generated (borderline)"
            else:
                score = 0
                details = f"ML classifier: {real_prob:.0%} probability human-written"

            signal = DetectionSignal(name=name, score=round(score, 2), details=details)

        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as exc:
            logger.warning("ML classifier API call failed", error=str(exc))
            signal = DetectionSignal(name=name, score=0, details="ML classifier unavailable")
        except Exception as exc:
            logger.warning("ML classifier unexpected error", error=str(exc))
            signal = DetectionSignal(name=name, score=0, details="ML classifier unavailable")

        self._ml_cache[text_hash] = signal
        return signal

    def _signal_perplexity_estimate(self, text: str) -> DetectionSignal:
        """Estimate text perplexity using character trigram surprise.
        Builds a trigram frequency model from the text and measures how
        'surprising' the text is character-by-character. AI text tends to
        have lower perplexity (more predictable character sequences)."""
        name = "Perplexity Estimate"

        if not text or len(text) < 200:
            return DetectionSignal(name=name, score=0, details="Not enough text for perplexity analysis")

        # Normalize text: lowercase, collapse whitespace
        cleaned = re.sub(r"\s+", " ", text.lower().strip())

        # Expected English character trigram distribution baselines
        # (derived from large English corpora — common trigrams and their
        # approximate relative frequencies)
        _english_common_trigrams = {
            "the": 3.5, "ing": 2.1, "and": 1.9, "ion": 1.6, "ent": 1.3,
            "tio": 1.5, "ati": 1.2, "for": 1.1, "her": 1.0, "ter": 1.0,
            "hat": 0.9, "tha": 0.9, "ere": 0.9, "ate": 0.8, "his": 0.8,
            "con": 0.8, "res": 0.7, "ver": 0.7, "all": 0.7, "ons": 0.7,
            "nce": 0.6, "men": 0.6, "ith": 0.6, "ted": 0.6, "ers": 0.6,
            "pro": 0.5, "thi": 0.5, "wit": 0.5, "are": 0.5, "ess": 0.5,
            "not": 0.5, "ive": 0.5, "was": 0.5, "ect": 0.5, "rea": 0.5,
            "com": 0.5, "eve": 0.4, "int": 0.4, "est": 0.4, "sta": 0.4,
            "ene": 0.4, "ous": 0.4, "ght": 0.4, "igh": 0.4, "ble": 0.4,
        }

        # Build character trigram model from the text itself
        text_trigrams: Counter[str] = Counter()
        for i in range(len(cleaned) - 2):
            tri = cleaned[i:i + 3]
            if tri.strip():  # skip whitespace-only trigrams
                text_trigrams[tri] += 1

        total_trigrams = sum(text_trigrams.values())
        if total_trigrams < 50:
            return DetectionSignal(name=name, score=0, details="Not enough character data")

        # Calculate cross-entropy against English baseline
        # For each common English trigram, compare observed vs expected frequency
        observed_freqs: dict[str, float] = {
            tri: count / total_trigrams * 100
            for tri, count in text_trigrams.items()
        }

        # Measure divergence: how much does this text deviate from English norms?
        kl_divergence = 0.0
        matched_trigrams = 0
        for tri, expected_freq in _english_common_trigrams.items():
            observed = observed_freqs.get(tri, 0.001)  # smoothing
            if observed > 0:
                ratio = observed / expected_freq
                kl_divergence += abs(math.log2(max(ratio, 0.001)))
                matched_trigrams += 1

        if matched_trigrams == 0:
            return DetectionSignal(name=name, score=0, details="Could not compute perplexity")

        avg_divergence = kl_divergence / matched_trigrams

        # Calculate self-perplexity: how predictable are the trigram sequences?
        # Lower self-entropy = more repetitive/predictable = more AI-like
        trigram_probs = {tri: count / total_trigrams for tri, count in text_trigrams.items()}
        self_entropy = -sum(p * math.log2(p) for p in trigram_probs.values() if p > 0)

        # Normalize self-entropy by max possible entropy
        max_possible_entropy = math.log2(len(text_trigrams)) if len(text_trigrams) > 1 else 1
        normalized_entropy = self_entropy / max_possible_entropy if max_possible_entropy > 0 else 0

        # Combine: low divergence from English norms + low self-entropy = AI-like
        # AI text closely matches expected distributions AND is internally predictable
        combined_score = (avg_divergence * 0.4) + (normalized_entropy * 0.6)

        # Thresholds calibrated: AI text typically scores < 0.65, human > 0.75
        if combined_score < 0.55:
            score = MAX_SIGNAL_SCORE
            details = f"Very low perplexity (score: {combined_score:.2f}). Text is highly predictable — AI-typical."
        elif combined_score < 0.65:
            score = MAX_SIGNAL_SCORE * 0.7
            details = f"Low perplexity (score: {combined_score:.2f}). Text is somewhat predictable."
        elif combined_score < 0.75:
            score = MAX_SIGNAL_SCORE * 0.35
            details = f"Moderate perplexity (score: {combined_score:.2f}). Borderline predictability."
        else:
            score = 0
            details = f"Natural perplexity (score: {combined_score:.2f}). Text has human-like unpredictability."

        return DetectionSignal(name=name, score=round(score, 2), details=details)

    def generate_heatmap(
        self, full_text: str, bullet_analyses: list[BulletAnalysis],
    ) -> list[HeatmapItem]:
        """Generate a heatmap of risk scores for each analyzed bullet."""
        heatmap: list[HeatmapItem] = []
        for ba in bullet_analyses:
            risk = 0.0
            # Factor 1: number of flags (each flag adds 0.2, capped contribution at 0.6)
            flag_contribution = min(len(ba.flags) * 0.2, 0.6)
            risk += flag_contribution
            # Factor 2: banned phrases found (each adds 0.15, capped at 0.3)
            phrase_contribution = min(len(ba.banned_phrases_found) * 0.15, 0.3)
            risk += phrase_contribution
            # Factor 3: structure type penalty for overly uniform patterns
            if ba.structure_type in ("action_metric", "action_result_metric"):
                risk += 0.1
            # Factor 4: ends with metric (common AI pattern)
            if ba.ends_with_metric:
                risk += 0.1

            risk = round(min(risk, 1.0), 2)

            if risk < 0.2:
                color = "green"
            elif risk < 0.5:
                color = "yellow"
            elif risk < 0.75:
                color = "orange"
            else:
                color = "red"

            heatmap.append(HeatmapItem(
                text=ba.text,
                risk=risk,
                flags=ba.flags,
                color=color,
            ))
        return heatmap

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
