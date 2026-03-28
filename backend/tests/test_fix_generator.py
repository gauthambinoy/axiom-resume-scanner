import pytest
from app.engines.ats_engine import ATSEngine
from app.engines.ai_detection_engine import AIDetectionEngine
from app.engines.keyword_extractor import KeywordExtractor
from app.engines.section_parser import SectionParser
from app.engines.fix_generator import FixGenerator


@pytest.fixture
def generator():
    return FixGenerator()


def test_generates_keyword_fixes(generator, sample_jd, ai_heavy_resume):
    extractor = KeywordExtractor()
    parser = SectionParser()
    ats_engine = ATSEngine()
    ai_engine = AIDetectionEngine()

    keywords = extractor.extract(sample_jd)
    sections = parser.parse(ai_heavy_resume)
    ats_result = ats_engine.score(ai_heavy_resume, sample_jd, sections, keywords)
    ai_result = ai_engine.analyze(ai_heavy_resume, sections, sections.bullets)

    fixes = generator.generate(ats_result, ai_result, sections)
    assert len(fixes) > 0
    categories = {f.category for f in fixes}
    assert "ats_keyword" in categories or "ai_detection" in categories


def test_fixes_sorted_by_priority(generator, sample_resume, sample_jd):
    extractor = KeywordExtractor()
    parser = SectionParser()
    ats_engine = ATSEngine()
    ai_engine = AIDetectionEngine()

    keywords = extractor.extract(sample_jd)
    sections = parser.parse(sample_resume)
    ats_result = ats_engine.score(sample_resume, sample_jd, sections, keywords)
    ai_result = ai_engine.analyze(sample_resume, sections, sections.bullets)

    fixes = generator.generate(ats_result, ai_result, sections)
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    for i in range(len(fixes) - 1):
        assert priority_order.get(fixes[i].priority, 4) <= priority_order.get(fixes[i + 1].priority, 4)


def test_max_25_fixes(generator, sample_jd, ai_heavy_resume):
    extractor = KeywordExtractor()
    parser = SectionParser()
    ats_engine = ATSEngine()
    ai_engine = AIDetectionEngine()

    keywords = extractor.extract(sample_jd)
    sections = parser.parse(ai_heavy_resume)
    ats_result = ats_engine.score(ai_heavy_resume, sample_jd, sections, keywords)
    ai_result = ai_engine.analyze(ai_heavy_resume, sections, sections.bullets)

    fixes = generator.generate(ats_result, ai_result, sections)
    assert len(fixes) <= 25
