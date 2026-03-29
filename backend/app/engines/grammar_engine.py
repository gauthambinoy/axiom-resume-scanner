"""
Grammar Engine -- detects common grammar, spelling, style, and punctuation issues.

Uses regex-based pattern matching to identify:
  - Double spaces
  - Missing capitalization after periods
  - Common misspellings / confusables
  - Repeated words
  - Sentence fragments
  - Run-on sentences
  - Passive voice overuse
  - Comma splices
  - Subject-verb agreement patterns
"""

import re
from dataclasses import dataclass, field


@dataclass
class GrammarIssue:
    type: str  # spelling, grammar, style, punctuation
    severity: str  # error, warning, suggestion
    message: str
    context: str  # the sentence/phrase with the issue
    suggestion: str  # how to fix it


@dataclass
class GrammarResult:
    overall_score: int = 100  # 0-100 (100 = perfect)
    issues: list[GrammarIssue] = field(default_factory=list)
    issue_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    suggestion_count: int = 0


# Common confusable word pairs and their contexts
_CONFUSABLES = [
    # (pattern, type, severity, message, suggestion)
    (
        r"\btheir\s+(?:is|was|are|were|has|have)\b",
        "spelling", "error",
        "Possible confusion of 'their' (possessive) with 'there' (location/existence).",
        "Consider using 'there' instead of 'their' before a verb.",
    ),
    (
        r"\bthere\s+(?:car|house|team|resume|work|experience|skills|education|project)\b",
        "spelling", "error",
        "Possible confusion of 'there' with 'their' (possessive).",
        "Consider using 'their' to show possession.",
    ),
    (
        r"\byour\s+(?:welcome|right|wrong|correct|the\s+best)\b",
        "spelling", "error",
        "Possible confusion of 'your' (possessive) with 'you're' (you are).",
        "Consider using 'you're' (you are) instead of 'your'.",
    ),
    (
        r"\bits\s+(?:important|clear|obvious|necessary|a\s+)\b",
        "spelling", "warning",
        "Possible confusion of 'its' (possessive) with 'it's' (it is).",
        "Consider using 'it's' (it is) if you mean 'it is'.",
    ),
    (
        r"\baffect\s+(?:on|of)\b",
        "spelling", "error",
        "Possible confusion of 'affect' (verb) with 'effect' (noun).",
        "Use 'effect on/of' (noun) instead of 'affect on/of'.",
    ),
    (
        r"\beffect(?:ed|ing)\s+(?:change|improvement|outcome)\b",
        "spelling", "warning",
        "Possible confusion: 'effected' means 'brought about'; did you mean 'affected'?",
        "Use 'affected' if you mean 'influenced' or 'impacted'.",
    ),
    (
        r"\bthen\s+(?:expected|anticipated|planned)\b",
        "spelling", "error",
        "Possible confusion of 'then' (time) with 'than' (comparison).",
        "Use 'than' for comparisons (e.g., 'better than expected').",
    ),
    (
        r"\blose\s+(?:fitting|leaf|change)\b",
        "spelling", "error",
        "Possible confusion of 'lose' (to misplace) with 'loose' (not tight).",
        "Use 'loose' if you mean 'not tight' or 'not fixed'.",
    ),
    (
        r"\bprincipal\s+(?:of|reason|idea|concept)\b",
        "spelling", "warning",
        "Possible confusion of 'principal' (main/person) with 'principle' (rule/concept).",
        "Use 'principle' for a rule, belief, or concept.",
    ),
]

# Passive voice indicators
_PASSIVE_PATTERN = re.compile(
    r"\b(?:is|are|was|were|been|being|be)\s+"
    r"(?:being\s+)?"
    r"(?:\w+ed|written|built|driven|given|taken|made|done|shown|known|seen|gone|run|set|put|cut|shut|held|kept|left|led|lost|met|paid|read|said|sent|sold|shot|stood|told|thought|understood|won)\b",
    re.IGNORECASE,
)

# Comma splice: sentence, sentence (without conjunction)
_COMMA_SPLICE_PATTERN = re.compile(
    r"[a-z]{2,}\s*,\s+(?:I|he|she|it|we|they|the|this|that|these|those|my|his|her|our|there)\s+[a-z]+",
    re.IGNORECASE,
)

# Repeated words
_REPEATED_WORD_PATTERN = re.compile(r"\b(\w{2,})\s+\1\b", re.IGNORECASE)

# Double spaces
_DOUBLE_SPACE_PATTERN = re.compile(r"  +")

# Missing capitalization after period
_MISSING_CAP_PATTERN = re.compile(r"\.\s+[a-z]")

# Subject-verb disagreement patterns
_SV_DISAGREEMENT = [
    (re.compile(r"\b(?:he|she|it)\s+(?:have|are|were)\b", re.IGNORECASE),
     "Subject-verb disagreement detected.",
     "Use 'has' with 'he/she/it', or 'is/was' instead of 'are/were'."),
    (re.compile(r"\b(?:they|we|I)\s+(?:has|is|was)\b", re.IGNORECASE),
     "Subject-verb disagreement detected.",
     "Use 'have' with 'they/we', or 'are/were' instead of 'is/was'. Use 'am/was' with 'I'."),
]


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, handling bullets and line breaks."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    result = []
    for s in sentences:
        lines = s.split("\n")
        for line in lines:
            stripped = line.strip()
            stripped = re.sub(r"^[*\-]\s*", "", stripped).strip()
            if stripped:
                result.append(stripped)
    return result


class GrammarEngine:
    """Regex-based grammar and writing quality checker."""

    def analyze(self, text: str) -> GrammarResult:
        if not text or not text.strip():
            return GrammarResult(overall_score=100)

        issues: list[GrammarIssue] = []
        sentences = _split_sentences(text)

        # 1. Double spaces
        for match in _DOUBLE_SPACE_PATTERN.finditer(text):
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end].strip()
            issues.append(GrammarIssue(
                type="punctuation",
                severity="warning",
                message="Double (or multiple) spaces detected.",
                context=context,
                suggestion="Replace with a single space.",
            ))

        # 2. Missing capitalization after periods
        for match in _MISSING_CAP_PATTERN.finditer(text):
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 20)
            context = text[start:end].strip()
            # Skip common abbreviations
            before = text[max(0, match.start() - 5):match.start() + 1]
            if re.search(r"\b(?:vs|etc|e\.g|i\.e|Mr|Mrs|Dr|Jr|Sr|St)\.", before, re.IGNORECASE):
                continue
            issues.append(GrammarIssue(
                type="punctuation",
                severity="error",
                message="Missing capitalization after period.",
                context=context,
                suggestion="Capitalize the first letter of the new sentence.",
            ))

        # 3. Common confusable words
        for pattern, issue_type, severity, message, suggestion in _CONFUSABLES:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - 15)
                end = min(len(text), match.end() + 15)
                context = text[start:end].strip()
                issues.append(GrammarIssue(
                    type=issue_type,
                    severity=severity,
                    message=message,
                    context=context,
                    suggestion=suggestion,
                ))

        # 4. Repeated words
        for match in _REPEATED_WORD_PATTERN.finditer(text):
            word = match.group(1)
            # Skip intentional repetitions
            if word.lower() in {"had", "that", "very", "so", "no"}:
                continue
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 10)
            context = text[start:end].strip()
            issues.append(GrammarIssue(
                type="grammar",
                severity="error",
                message=f"Repeated word: '{word} {word}'.",
                context=context,
                suggestion=f"Remove the duplicate '{word}'.",
            ))

        # 5. Sentence fragments (very short sentences < 4 words, not bullets)
        for sentence in sentences:
            words = sentence.split()
            # Skip bullet-style items, headings, dates, etc.
            if len(words) < 4 and len(words) >= 1:
                # Heuristic: skip if it looks like a heading, date, or label
                if re.match(r"^[A-Z][a-z]+\s*[:|\-]", sentence):
                    continue
                if re.match(r"^\d", sentence):
                    continue
                if len(sentence) < 10:
                    continue
                # Looks like a fragment
                issues.append(GrammarIssue(
                    type="style",
                    severity="suggestion",
                    message="Possible sentence fragment (very short sentence).",
                    context=sentence,
                    suggestion="Consider expanding into a complete sentence or merging with adjacent text.",
                ))

        # 6. Run-on sentences (> 50 words without punctuation break)
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 50:
                # Check if there's a mid-sentence break (semicolon, em dash)
                if not re.search(r"[;:\u2014]", sentence):
                    truncated = " ".join(words[:15]) + "..."
                    issues.append(GrammarIssue(
                        type="style",
                        severity="warning",
                        message=f"Possible run-on sentence ({len(words)} words without punctuation break).",
                        context=truncated,
                        suggestion="Break into shorter sentences or add punctuation (semicolons, em dashes).",
                    ))

        # 7. Passive voice overuse
        passive_count = 0
        passive_examples: list[str] = []
        for sentence in sentences:
            matches = _PASSIVE_PATTERN.findall(sentence)
            if matches:
                passive_count += 1
                if len(passive_examples) < 3:
                    truncated = sentence[:80] + ("..." if len(sentence) > 80 else "")
                    passive_examples.append(truncated)

        if sentences and passive_count / max(len(sentences), 1) > 0.3:
            for example in passive_examples:
                issues.append(GrammarIssue(
                    type="style",
                    severity="suggestion",
                    message="Passive voice detected. Overuse of passive voice can weaken writing.",
                    context=example,
                    suggestion="Consider rewriting in active voice for stronger, more direct language.",
                ))

        # 8. Comma splices
        for sentence in sentences:
            for match in _COMMA_SPLICE_PATTERN.finditer(sentence):
                start = max(0, match.start() - 10)
                end = min(len(sentence), match.end() + 20)
                context = sentence[start:end].strip()
                issues.append(GrammarIssue(
                    type="grammar",
                    severity="warning",
                    message="Possible comma splice (two independent clauses joined by a comma).",
                    context=context,
                    suggestion="Use a semicolon, period, or add a conjunction (and, but, so).",
                ))

        # 9. Subject-verb agreement
        for pattern, message, suggestion in _SV_DISAGREEMENT:
            for match in pattern.finditer(text):
                start = max(0, match.start() - 15)
                end = min(len(text), match.end() + 15)
                context = text[start:end].strip()
                issues.append(GrammarIssue(
                    type="grammar",
                    severity="error",
                    message=message,
                    context=context,
                    suggestion=suggestion,
                ))

        # Deduplicate issues with the same context + message
        seen = set()
        unique_issues: list[GrammarIssue] = []
        for issue in issues:
            key = (issue.message, issue.context)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        issues = unique_issues

        # Calculate score
        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")
        suggestion_count = sum(1 for i in issues if i.severity == "suggestion")

        # Scoring: errors=-5, warnings=-3, suggestions=-1, min 0
        penalty = error_count * 5 + warning_count * 3 + suggestion_count * 1
        overall_score = max(0, 100 - penalty)

        return GrammarResult(
            overall_score=overall_score,
            issues=issues,
            issue_count=len(issues),
            error_count=error_count,
            warning_count=warning_count,
            suggestion_count=suggestion_count,
        )
