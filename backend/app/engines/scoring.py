from dataclasses import dataclass

from app.engines.ats_engine import ATSScoreResult
from app.engines.ai_detection_engine import AIDetectionResult


@dataclass
class CombinedScore:
    interview_readiness_score: int = 0
    readiness_level: str = "AT_RISK"  # INTERVIEW_READY, NEEDS_WORK, AT_RISK
    competitor_percentile: int = 50
    ats_weight: float = 0.6
    ai_weight: float = 0.4
    chart_data: dict[str, int | float | str] | None = None


class ScoreNormalizer:
    AVERAGE_ATS_SCORE = 55  # Recalibrated: most resumes score lower than expected
    ATS_STD_DEV = 18        # Wider spread for more granular percentiles

    def combine(self, ats: ATSScoreResult, ai: AIDetectionResult) -> CombinedScore:
        result = CombinedScore()

        ats_score = ats.overall_score
        ai_score = ai.overall_score

        # Tighter readiness thresholds — INTERVIEW_READY should be hard to earn
        if ats_score >= 80 and ai_score < 25:
            result.readiness_level = "INTERVIEW_READY"
        elif ats_score >= 65 and ai_score < 40:
            result.readiness_level = "NEEDS_WORK"
        else:
            result.readiness_level = "AT_RISK"

        # Combined score with AI penalty curve — high AI scores penalize MORE
        ai_inverted = max(0, 100 - ai_score)
        # Apply penalty multiplier: AI score > 50 gets extra penalty
        if ai_score > 50:
            ai_penalty = (ai_score - 50) * 0.3  # Extra penalty for high AI
            ai_inverted = max(0, ai_inverted - ai_penalty)

        result.interview_readiness_score = round(ats_score * 0.6 + ai_inverted * 0.4)
        result.interview_readiness_score = min(100, max(0, result.interview_readiness_score))

        # Competitor percentile (based on normal distribution approximation)
        z_score = (ats_score - self.AVERAGE_ATS_SCORE) / max(self.ATS_STD_DEV, 1)
        result.competitor_percentile = self._z_to_percentile(z_score)

        result.chart_data = {
            "ats_score": ats_score,
            "ai_score": round(ai_score, 1),
            "combined": result.interview_readiness_score,
            "ats_grade": ats.grade,
            "ai_risk": ai.risk_level,
            "readiness": result.readiness_level,
        }

        return result

    def _z_to_percentile(self, z: float) -> int:
        # Simple approximation of CDF
        import math
        percentile = 50 * (1 + math.erf(z / math.sqrt(2)))
        return min(99, max(1, round(percentile)))
