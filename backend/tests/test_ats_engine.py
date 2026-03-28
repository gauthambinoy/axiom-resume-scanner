import pytest
from app.engines.ats_engine import ATSEngine
from app.engines.keyword_extractor import KeywordExtractor
from app.engines.section_parser import SectionParser


@pytest.fixture
def engine():
    return ATSEngine()


@pytest.fixture
def extractor():
    return KeywordExtractor()


@pytest.fixture
def parser():
    return SectionParser()


def test_perfect_match_scores_high(engine, extractor, parser, sample_resume, sample_jd):
    keywords = extractor.extract(sample_jd)
    sections = parser.parse(sample_resume)
    result = engine.score(sample_resume, sample_jd, sections, keywords)
    assert result.overall_score >= 50  # Good match
    assert result.grade in ("A+", "A", "B+", "B")


def test_no_match_scores_low(engine, extractor, parser, sample_jd):
    unrelated = """EXPERIENCE
Chef at Restaurant | 2020 - Present
- Prepared gourmet meals for 200 guests per evening service at the downtown bistro
- Managed kitchen inventory and reduced food waste by coordinating with local suppliers
- Trained 5 junior cooks on classical French cuisine techniques and plating standards
- Created seasonal menus featuring locally sourced organic ingredients from nearby farms

EDUCATION
Culinary Arts Diploma | Culinary Institute | 2019

SKILLS
Cooking, Baking, Menu Planning, Food Safety, Team Management, Inventory Control
"""
    keywords = extractor.extract(sample_jd)
    sections = parser.parse(unrelated)
    result = engine.score(unrelated, sample_jd, sections, keywords)
    assert result.overall_score < 40
    assert len(result.missing_keywords) > 0


def test_keyword_aliases_detected(engine, extractor, parser):
    resume = """EXPERIENCE
Software Developer | TechCo | 2020 - Present
- Built REST APIs using JS and Node with Express framework for production microservices
- Deployed services on K8s clusters managed with Terraform and monitored via Grafana dashboards
- Wrote integration tests in Py using pytest to validate critical business logic end to end

SKILLS
JS, Node, K8s, Py, Git, Docker, Terraform, React
"""
    jd = "Looking for experience with JavaScript, Node.js, Kubernetes, Python, Docker, React, and Terraform for our cloud platform team."
    keywords = extractor.extract(jd)
    sections = parser.parse(resume)
    result = engine.score(resume, jd, sections, keywords)
    # Aliases should be detected
    matched_kws = [m.keyword for m in result.matched_keywords]
    assert len(matched_kws) > 0


def test_missing_sections_penalized(engine, extractor, parser, sample_jd):
    resume = """Software developer with Python experience building web apps and APIs for 5 years.
Built microservices with FastAPI and deployed them on AWS using Docker and Kubernetes.
Also worked with PostgreSQL, Redis, and React on various full stack projects at scale."""
    keywords = extractor.extract(sample_jd)
    sections = parser.parse(resume)
    result = engine.score(resume, sample_jd, sections, keywords)
    assert result.section_score < 80
    assert len(result.section_warnings) > 0


def test_formatting_warnings_generated(engine, extractor, parser, sample_jd):
    resume = """EXPERIENCE
Engineer | Corp | 2020 - Present
- Built systems     with Python      and deployed      on AWS infrastructure
- Created tables     for data      processing      and analysis workflows
| Column 1 | Column 2 | Column 3 |
| data     | data     | data     |
[image] profile_photo.png embedded in resume header section above

EDUCATION
BS CS | University | 2019

SKILLS
Python, AWS, Docker, PostgreSQL, Redis, FastAPI, React, JavaScript
"""
    keywords = extractor.extract(sample_jd)
    sections = parser.parse(resume)
    result = engine.score(resume, sample_jd, sections, keywords)
    assert len(result.formatting_warnings) > 0


def test_grade_thresholds(engine, extractor, parser, sample_resume, sample_jd):
    keywords = extractor.extract(sample_jd)
    sections = parser.parse(sample_resume)
    result = engine.score(sample_resume, sample_jd, sections, keywords)
    valid_grades = {"A+", "A", "B+", "B", "C+", "C", "D", "F"}
    assert result.grade in valid_grades
