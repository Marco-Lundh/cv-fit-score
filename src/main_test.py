from http import HTTPStatus
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models import FitScoreResponse

_MOCK_RESPONSE = FitScoreResponse(
    match_score=72,
    strengths=["Python", "FastAPI"],
    weaknesses=["Missing k8s"],
    recommendations=["Learn k8s"],
    summary="Good fit overall.",
)


async def test_health_check():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


async def test_index_returns_html():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert "text/html" in response.headers["content-type"]


async def test_analyze_text_success():
    with (
        patch(
            "src.main.scrape_job_description",
            new_callable=AsyncMock,
            return_value="Software engineer job description.",
        ),
        patch(
            "src.main.analyze_fit",
            new_callable=AsyncMock,
            return_value=_MOCK_RESPONSE,
        ),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/analyze/text",
                json={
                    "cv_text": "a" * 50,
                    "job_url": "https://example.com/jobs/1",
                    "language": "en",
                },
            )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["match_score"] == 72


async def test_analyze_text_cv_too_short():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/analyze/text",
            json={
                "cv_text": "short",
                "job_url": "https://example.com/jobs/1",
            },
        )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_analyze_text_scrape_failure_returns_422():
    with patch(
        "src.main.scrape_job_description",
        new_callable=AsyncMock,
        side_effect=Exception("Connection refused"),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/analyze/text",
                json={
                    "cv_text": "a" * 50,
                    "job_url": "https://example.com/jobs/1",
                },
            )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "Failed to fetch job URL" in response.json()["detail"]


async def test_analyze_pdf_wrong_content_type():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/analyze/pdf",
            data={"job_url": "https://example.com/jobs/1"},
            files={"cv_file": ("cv.txt", b"not a pdf", "text/plain")},
        )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "PDF" in response.json()["detail"]


async def test_analyze_pdf_success():
    with (
        patch(
            "src.main.extract_text_from_pdf",
            return_value="Extracted CV content.",
        ),
        patch(
            "src.main.scrape_job_description",
            new_callable=AsyncMock,
            return_value="Job description content.",
        ),
        patch(
            "src.main.analyze_fit",
            new_callable=AsyncMock,
            return_value=_MOCK_RESPONSE,
        ),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/analyze/pdf",
                data={"job_url": "https://example.com/jobs/1"},
                files={
                    "cv_file": ("cv.pdf", b"fake pdf bytes", "application/pdf")
                },
            )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["match_score"] == 72
