import pytest
from tests.conftest import SAMPLE_RESUME, SAMPLE_JD


@pytest.mark.asyncio
async def test_scan_endpoint_success(client):
    response = await client.post("/api/v1/scan", json={
        "resume_text": SAMPLE_RESUME,
        "jd_text": SAMPLE_JD,
    })
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert "ats_score" in data
    assert "ai_score" in data


@pytest.mark.asyncio
async def test_scan_endpoint_validation_error(client):
    response = await client.post("/api/v1/scan", json={
        "resume_text": "too short",
        "jd_text": "too short",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_stats_endpoint(client):
    response = await client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data


@pytest.mark.asyncio
async def test_banned_phrases_endpoint(client):
    response = await client.get("/api/v1/banned-phrases")
    assert response.status_code == 200
    data = response.json()
    assert len(data["banned_phrases"]) > 0
    assert len(data["banned_words"]) > 0


@pytest.mark.asyncio
async def test_quick_scan_endpoint(client):
    response = await client.post("/api/v1/scan/quick", json={
        "resume_text": SAMPLE_RESUME,
        "jd_text": SAMPLE_JD,
    })
    assert response.status_code == 200
    data = response.json()
    assert "ats_keyword_score" in data


@pytest.mark.asyncio
async def test_compare_endpoint(client):
    response = await client.post("/api/v1/compare", json={
        "resume_before": SAMPLE_RESUME,
        "resume_after": SAMPLE_RESUME,
        "jd_text": SAMPLE_JD,
    })
    assert response.status_code == 200
    data = response.json()
    assert "before" in data
    assert "after" in data


@pytest.mark.asyncio
async def test_error_response_structure(client):
    response = await client.post("/api/v1/scan", json={
        "resume_text": "x",
        "jd_text": "y",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "ResumeShield" in response.json()["message"]
