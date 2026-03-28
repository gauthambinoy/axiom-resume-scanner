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
    AVERAGE_ATS_SCORE = 58
    ATS_STD_DEV = 15

    def combine(self, ats: ATSScoreResult, ai: AIDetectionResult) -> CombinedScore:
        result = CombinedScore()

        ats_score = ats.overall_score
        ai_score = ai.overall_score

        # Readiness level
        if ats_score > 75 and ai_score < 30:
            result.readiness_level = "INTERVIEW_READY"
        elif ats_score > 60 and ai_score < 50:
            result.readiness_level = "NEEDS_WORK"
        else:
            result.readiness_level = "AT_RISK"

        # Combined score: high ATS is good, low AI is good
        ai_inverted = max(0, 100 - ai_score)
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
