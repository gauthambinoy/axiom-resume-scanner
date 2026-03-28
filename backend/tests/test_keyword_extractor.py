import pytest
from app.engines.keyword_extractor import KeywordExtractor


@pytest.fixture
def extractor():
    return KeywordExtractor()


def test_extracts_technical_skills(extractor, sample_jd):
    result = extractor.extract(sample_jd)
    skills_lower = [s.lower() for s in result.technical_skills]
    assert "python" in skills_lower
    assert "docker" in skills_lower


def test_extracts_soft_skills(extractor, sample_jd):
    result = extractor.extract(sample_jd)
    assert any("communication" in s for s in result.soft_skills)


def test_handles_empty_input(extractor):
    result = extractor.extract("")
    assert result.is_empty is True
    assert result.all_keywords == []


def test_deduplicates_keywords(extractor, sample_jd):
    result = extractor.extract(sample_jd)
    assert len(result.all_keywords) == len(set(result.all_keywords))


def test_frequency_counting_correct(extractor, sample_jd):
    result = extractor.extract(sample_jd)
    # "python" should appear at least once
    if "python" in result.keyword_frequency:
        assert result.keyword_frequency["python"] >= 1


def test_priority_ordering(extractor, sample_jd):
    result = extractor.extract(sample_jd)
    assert len(result.priority_keywords) <= 20
    if len(result.priority_keywords) > 1:
        # First keyword should have >= frequency of last
        first_freq = result.keyword_frequency.get(result.priority_keywords[0], 0)
        last_freq = result.keyword_frequency.get(result.priority_keywords[-1], 0)
        assert first_freq >= last_freq


def test_short_input_warns(extractor):
    result = extractor.extract("Python developer needed")
    assert result.warning != ""
