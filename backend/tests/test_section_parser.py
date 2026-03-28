import pytest
from app.engines.section_parser import SectionParser
from app.utils.exceptions import ResumeEmptyError


@pytest.fixture
def parser():
    return SectionParser()


def test_detects_all_caps_headers(parser, sample_resume):
    result = parser.parse(sample_resume)
    found_lower = [s.lower() for s in result.sections_found]
    assert any("summary" in s for s in found_lower) or any("experience" in s for s in found_lower)


def test_extracts_bullets_correctly(parser, sample_resume):
    result = parser.parse(sample_resume)
    assert result.total_bullet_count > 0
    assert all(b.word_count > 0 for b in result.bullets)


def test_counts_words_per_bullet(parser, sample_resume):
    result = parser.parse(sample_resume)
    for b in result.bullets:
        assert b.word_count == len(b.text.split())


def test_identifies_missing_sections(parser):
    minimal = """EXPERIENCE
- Did some work on projects using Python and JavaScript for 5 years at a major company
- Built another thing that was really cool and useful and used by many people daily
"""
    result = parser.parse(minimal)
    assert len(result.sections_missing) > 0


def test_handles_empty_raises_error(parser):
    with pytest.raises(ResumeEmptyError):
        parser.parse("")


def test_handles_no_sections_gracefully(parser):
    text = """Just a plain text resume without any headers or sections.
    I have 5 years of experience working with Python and building web applications.
    I know Docker, Kubernetes, and AWS. I went to State University for Computer Science."""
    result = parser.parse(text)
    assert result.flat_text_mode is True
    assert "Could not detect section headers" in result.warnings


def test_detects_contact_info(parser, sample_resume):
    result = parser.parse(sample_resume)
    assert result.contact_info.email == "john.doe@email.com"


def test_detects_metrics_in_bullets(parser, sample_resume):
    result = parser.parse(sample_resume)
    metric_bullets = [b for b in result.bullets if b.has_metric]
    assert len(metric_bullets) > 0
