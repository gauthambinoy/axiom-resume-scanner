import pytest
from app.engines.ai_detection_engine import AIDetectionEngine
from app.engines.section_parser import SectionParser


@pytest.fixture
def engine():
    return AIDetectionEngine()


@pytest.fixture
def parser():
    return SectionParser()


def test_human_written_scores_low(engine, parser, sample_resume):
    sections = parser.parse(sample_resume)
    result = engine.analyze(sample_resume, sections, sections.bullets)
    # Well-written human resume should score low
    assert result.overall_score < 50
    assert result.risk_level in ("LOW", "MODERATE")


def test_ai_written_scores_high(engine, parser, ai_heavy_resume):
    sections = parser.parse(ai_heavy_resume)
    result = engine.analyze(ai_heavy_resume, sections, sections.bullets)
    # AI-heavy resume should score higher
    assert result.overall_score > 25
    assert result.risk_level in ("MODERATE", "HIGH", "CRITICAL")


def test_banned_phrases_detected(engine, parser, ai_heavy_resume):
    sections = parser.parse(ai_heavy_resume)
    result = engine.analyze(ai_heavy_resume, sections, sections.bullets)
    phrase_signal = next((s for s in result.signals if s.name == "Banned Phrase Density"), None)
    assert phrase_signal is not None
    assert phrase_signal.score > 0
    assert len(phrase_signal.flagged_items) > 0


def test_opening_word_repetition_detected(engine, parser, ai_heavy_resume):
    sections = parser.parse(ai_heavy_resume)
    result = engine.analyze(ai_heavy_resume, sections, sections.bullets)
    opener_signal = next((s for s in result.signals if s.name == "Opening Word Repetition"), None)
    assert opener_signal is not None
    assert opener_signal.score > 0


def test_structure_uniformity_detected(engine, parser, ai_heavy_resume):
    sections = parser.parse(ai_heavy_resume)
    result = engine.analyze(ai_heavy_resume, sections, sections.bullets)
    struct_signal = next((s for s in result.signals if s.name == "Structure Uniformity"), None)
    assert struct_signal is not None
    assert struct_signal.score > 0


def test_round_numbers_flagged(engine, parser, ai_heavy_resume):
    sections = parser.parse(ai_heavy_resume)
    result = engine.analyze(ai_heavy_resume, sections, sections.bullets)
    round_signal = next((s for s in result.signals if s.name == "Round Number Usage"), None)
    assert round_signal is not None
    assert round_signal.score > 0


def test_per_bullet_analysis_correct(engine, parser, sample_resume):
    sections = parser.parse(sample_resume)
    result = engine.analyze(sample_resume, sections, sections.bullets)
    assert len(result.per_bullet_analysis) == len(sections.bullets)
    for ba in result.per_bullet_analysis:
        assert ba.word_count > 0
        assert ba.ai_risk in ("clean", "suspicious", "flagged")


def test_summary_adjective_density(engine, parser, ai_heavy_resume):
    sections = parser.parse(ai_heavy_resume)
    result = engine.analyze(ai_heavy_resume, sections, sections.bullets)
    adj_signal = next((s for s in result.signals if s.name == "Summary Adjective Density"), None)
    assert adj_signal is not None
    assert adj_signal.score > 0


def test_twelve_signals_present(engine, parser, sample_resume):
    sections = parser.parse(sample_resume)
    result = engine.analyze(sample_resume, sections, sections.bullets)
    assert len(result.signals) == 12


def test_top_issues_populated(engine, parser, ai_heavy_resume):
    sections = parser.parse(ai_heavy_resume)
    result = engine.analyze(ai_heavy_resume, sections, sections.bullets)
    assert len(result.top_issues) > 0
