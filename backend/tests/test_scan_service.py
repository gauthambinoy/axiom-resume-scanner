import pytest
from app.services.scan_service import ScanService


@pytest.fixture
def service():
    return ScanService()


@pytest.mark.asyncio
async def test_full_pipeline_returns_complete_result(service, sample_resume, sample_jd):
    result = await service.scan(sample_resume, sample_jd)
    assert result.scan_id
    assert result.ats_score.overall_score >= 0
    assert result.ai_score.overall_score >= 0
    assert result.combined.interview_readiness_score >= 0
    assert len(result.metadata.engines_used) > 0
    assert result.metadata.processing_time_ms > 0


@pytest.mark.asyncio
async def test_quick_scan(service, sample_resume, sample_jd):
    result = await service.quick_scan(sample_resume, sample_jd)
    assert result.scan_id
    assert result.ats_keyword_score >= 0
    assert result.processing_time_ms > 0


@pytest.mark.asyncio
async def test_compare(service, sample_resume, ai_heavy_resume, sample_jd):
    result = await service.compare(ai_heavy_resume, sample_resume, sample_jd)
    assert result.before.scan_id != result.after.scan_id
    assert isinstance(result.ats_change, int)


@pytest.mark.asyncio
async def test_stats_tracking(service, sample_resume, sample_jd):
    await service.scan(sample_resume, sample_jd)
    stats = service.get_stats()
    assert stats["total_scans"] >= 1
