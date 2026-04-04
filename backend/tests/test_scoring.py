"""Tests for the ScoreNormalizer and CombinedScore logic."""
import pytest
from unittest.mock import MagicMock
from app.engines.scoring import ScoreNormalizer, CombinedScore


@pytest.fixture
def normalizer():
    return ScoreNormalizer()


def _make_ats(overall: int):
    m = MagicMock()
    m.overall_score = overall
    return m


def _make_ai(overall: int):
    m = MagicMock()
    m.overall_score = overall
    return m


class TestReadinessLevel:
    def test_interview_ready_when_high_ats_and_low_ai(self, normalizer):
        result = normalizer.combine(_make_ats(85), _make_ai(20))
        assert result.readiness_level == "INTERVIEW_READY"

    def test_needs_work_when_moderate_ats(self, normalizer):
        result = normalizer.combine(_make_ats(68), _make_ai(35))
        assert result.readiness_level == "NEEDS_WORK"

    def test_at_risk_when_low_ats(self, normalizer):
        result = normalizer.combine(_make_ats(40), _make_ai(60))
        assert result.readiness_level == "AT_RISK"

    def test_at_risk_when_high_ai_score(self, normalizer):
        # Even with decent ATS, high AI detection means AT_RISK
        result = normalizer.combine(_make_ats(80), _make_ai(55))
        assert result.readiness_level == "AT_RISK"


class TestCombinedScore:
    def test_combined_score_is_integer(self, normalizer):
        result = normalizer.combine(_make_ats(70), _make_ai(30))
        assert isinstance(result.interview_readiness_score, int)

    def test_high_ai_penalises_combined_score(self, normalizer):
        """A resume with the same ATS score but higher AI detection should score lower."""
        low_ai = normalizer.combine(_make_ats(70), _make_ai(10))
        high_ai = normalizer.combine(_make_ats(70), _make_ai(80))
        assert low_ai.interview_readiness_score > high_ai.interview_readiness_score

    def test_combined_score_bounded_0_to_100(self, normalizer):
        for ats_s, ai_s in [(0, 0), (100, 0), (0, 100), (100, 100), (50, 50)]:
            result = normalizer.combine(_make_ats(ats_s), _make_ai(ai_s))
            assert 0 <= result.interview_readiness_score <= 100

    def test_percentile_is_reasonable(self, normalizer):
        result = normalizer.combine(_make_ats(60), _make_ai(40))
        assert 0 <= result.competitor_percentile <= 100
