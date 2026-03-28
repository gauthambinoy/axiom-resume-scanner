from dataclasses import dataclass, field

from app.engines.ats_engine import ATSScoreResult
from app.engines.ai_detection_engine import AIDetectionResult
from app.engines.section_parser import SectionParseResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

BANNED_PHRASE_ALTERNATIVES: dict[str, str] = {
    "responsible for": "Owned / Ran / Drove",
    "in charge of": "Led / Directed",
    "helped with": "Contributed to / Supported",
    "worked on": "Shipped / Delivered / Built",
    "involved in": "Contributed to",
    "passionate about": "(remove — show through actions instead)",
    "results-driven": "(remove — show results directly)",
    "dynamic professional": "(remove — use a specific title instead)",
    "dedicated team player": "(remove — describe collaboration concretely)",
    "detail-oriented": "(remove — demonstrate via specific examples)",
    "seamless integration": "integration",
    "proven track record": "(remove — let metrics prove it)",
    "self-starter": "(remove — describe initiative concretely)",
    "thought leader": "(remove — list publications/talks instead)",
    "cutting-edge": "modern / current",
    "state-of-the-art": "modern / current",
    "robust solution": "solution",
    "best practices": "standards / patterns",
    "fast-paced environment": "(remove — generic filler)",
    "strong communication skills": "(remove — show communication outcomes)",
    "scalable architecture": "architecture (add specific scale numbers)",
    "cross-functional collaboration": "collaborated with [specific teams]",
    "actionable insights": "insights that led to [specific outcome]",
    "data-driven decision": "decision based on [specific data]",
}


@dataclass
class FixSuggestion:
    category: str  # ats_keyword, ai_detection, section, formatting
    priority: str  # critical, high, medium, low
    title: str
    description: str
    affected_bullets: list[int] = field(default_factory=list)
    impact: str = ""


class FixGenerator:
    def generate(
        self,
        ats_result: ATSScoreResult,
        ai_result: AIDetectionResult,
        sections: SectionParseResult,
    ) -> list[FixSuggestion]:
        try:
            fixes: list[FixSuggestion] = []
            fixes.extend(self._ats_keyword_fixes(ats_result))
            fixes.extend(self._ai_detection_fixes(ai_result))
            fixes.extend(self._section_fixes(ats_result, sections))
            fixes.extend(self._formatting_fixes(ats_result))

            # Sort by priority
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            fixes.sort(key=lambda f: priority_order.get(f.priority, 4))

            return fixes[:25]
        except Exception as e:
            logger.error("Fix generation failed", error=str(e))
            return []

    def _ats_keyword_fixes(self, ats: ATSScoreResult) -> list[FixSuggestion]:
        fixes: list[FixSuggestion] = []

        # Missing keywords
        for i, kw in enumerate(ats.missing_keywords[:10]):
            priority = "critical" if i < 3 else "high" if i < 7 else "medium"
            fixes.append(FixSuggestion(
                category="ats_keyword",
                priority=priority,
                title=f"Add missing keyword: '{kw}'",
                description=(
                    f"The keyword '{kw}' appears in the job description but is missing from "
                    f"your resume. Add it to an experience bullet showing how you used it, "
                    f"or to your skills section."
                ),
                impact=f"This fix will improve your ATS score by ~{max(2, 5 - i)} points",
            ))

        # Skills-only keywords
        for kw in ats.skills_only_keywords[:5]:
            fixes.append(FixSuggestion(
                category="ats_keyword",
                priority="high",
                title=f"Add context for '{kw}'",
                description=(
                    f"The keyword '{kw}' only appears in your skills section. Add it to a "
                    f"bullet point with context showing how you used it. Example: "
                    f"'Used {kw} to [achieve specific outcome]'."
                ),
                impact="This fix will improve your keyword placement score by ~3 points",
            ))

        return fixes

    def _ai_detection_fixes(self, ai: AIDetectionResult) -> list[FixSuggestion]:
        fixes: list[FixSuggestion] = []

        for signal in ai.signals:
            if signal.score < 2.0:
                continue

            priority = "critical" if signal.score >= 7 else "high" if signal.score >= 5 else "medium"

            if signal.name == "Sentence Length Variance":
                fixes.append(FixSuggestion(
                    category="ai_detection",
                    priority=priority,
                    title="Vary your bullet point lengths",
                    description=(
                        f"{signal.details}. Rewrite some bullets to be under 15 words "
                        f"and others over 40 words. Mix short punchy bullets with detailed ones."
                    ),
                    impact=f"This fix will reduce your AI detection score by ~{signal.score:.0f} points",
                ))

            elif signal.name == "Opening Word Repetition":
                fixes.append(FixSuggestion(
                    category="ai_detection",
                    priority=priority,
                    title="Diversify bullet opening words",
                    description=(
                        f"{signal.details}. Try starting some bullets with: the technical subject "
                        f"('The microservice...'), a context phrase ('Under tight deadlines...'), "
                        f"a number ('3 production incidents...'), or a gerund ('Debugging a...')."
                    ),
                    impact=f"This fix will reduce your AI detection score by ~{signal.score:.0f} points",
                ))

            elif signal.name == "Banned Phrase Density":
                for phrase in signal.flagged_items[:5]:
                    alt = BANNED_PHRASE_ALTERNATIVES.get(phrase, "(rephrase with specific details)")
                    fixes.append(FixSuggestion(
                        category="ai_detection",
                        priority="high",
                        title=f"Remove banned phrase: '{phrase}'",
                        description=f"Replace '{phrase}' with: {alt}",
                        impact="This fix will reduce your AI detection score by ~1 point",
                    ))

            elif signal.name == "Banned Word Density":
                for word in signal.flagged_items[:3]:
                    fixes.append(FixSuggestion(
                        category="ai_detection",
                        priority="medium",
                        title=f"Replace AI-flagged word: '{word}'",
                        description=f"The word '{word}' is flagged by AI detectors at anomalous rates. Use a simpler synonym.",
                        impact="This fix will reduce your AI detection score by ~1 point",
                    ))

            elif signal.name == "Structure Uniformity":
                fixes.append(FixSuggestion(
                    category="ai_detection",
                    priority=priority,
                    title="Break the Verb+Object+Metric pattern",
                    description=(
                        f"{signal.details}. Try starting some bullets with the technical "
                        f"subject ('The payment API serving 10K req/s...'), a constraint "
                        f"('Under a 2-week deadline...'), or skip the verb entirely "
                        f"('Primary on-call for the billing service, 99.95% uptime')."
                    ),
                    impact=f"This fix will reduce your AI detection score by ~{signal.score:.0f} points",
                ))

            elif signal.name == "Round Number Usage":
                fixes.append(FixSuggestion(
                    category="ai_detection",
                    priority=priority,
                    title="Use specific numbers instead of round ones",
                    description=(
                        f"{signal.details}. Replace round percentages (50%, 30%) with "
                        f"specific ones (47%, 31%) or use relative terms (~3x, halved)."
                    ),
                    impact=f"This fix will reduce your AI detection score by ~{signal.score:.0f} points",
                ))

            elif signal.name == "Metric Saturation":
                fixes.append(FixSuggestion(
                    category="ai_detection",
                    priority=priority,
                    title="Reduce metric-heavy endings",
                    description=(
                        f"{signal.details}. Not every bullet needs a number. End some with "
                        f"qualitative outcomes: 'earned praise from the VP of Eng', "
                        f"'became the team's go-to for debugging'."
                    ),
                    impact=f"This fix will reduce your AI detection score by ~{signal.score:.0f} points",
                ))

            elif signal.name == "Summary Adjective Density":
                fixes.append(FixSuggestion(
                    category="ai_detection",
                    priority=priority,
                    title="Reduce adjectives in summary",
                    description=(
                        f"{signal.details}. Remove self-descriptive adjectives like "
                        f"'experienced', 'passionate', 'dedicated'. Instead, state facts: "
                        f"'Backend engineer, 5 years, mostly Python + Go. Shipped [product].'"
                    ),
                    impact=f"This fix will reduce your AI detection score by ~{signal.score:.0f} points",
                ))

            elif signal.name == "Transitional Word Overuse":
                fixes.append(FixSuggestion(
                    category="ai_detection",
                    priority=priority,
                    title="Remove transitional openers",
                    description=(
                        f"{signal.details}. Words like 'Additionally', 'Furthermore', 'Moreover' "
                        f"are red flags. Just start the next bullet directly."
                    ),
                    impact=f"This fix will reduce your AI detection score by ~{signal.score:.0f} points",
                ))

        return fixes

    def _section_fixes(self, ats: ATSScoreResult, sections: SectionParseResult) -> list[FixSuggestion]:
        fixes: list[FixSuggestion] = []
        for warning in ats.section_warnings:
            section_name = warning.replace("Missing required section: ", "").replace("Missing recommended section: ", "")
            fixes.append(FixSuggestion(
                category="section",
                priority="high" if "required" in warning.lower() else "medium",
                title=f"Add {section_name} section",
                description=f"{warning}. This section is expected by ATS systems.",
                impact="This fix will improve your section structure score by ~5 points",
            ))
        return fixes

    def _formatting_fixes(self, ats: ATSScoreResult) -> list[FixSuggestion]:
        fixes: list[FixSuggestion] = []
        for warning in ats.formatting_warnings:
            fixes.append(FixSuggestion(
                category="formatting",
                priority="medium",
                title="Fix formatting issue",
                description=warning,
                impact="This fix will improve your formatting score by ~5 points",
            ))
        return fixes
