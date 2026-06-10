from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.services.scraper import scrape_job_description
from src.services.tls import SSL_CONTEXT

_JOB_HTML = """
<html><head><title>Software Engineer</title></head>
<body>
<nav>Navigation links here</nav>
<main>
We are looking for a Python developer with 3+ years experience.
You will work on FastAPI backends, Kubernetes deployments, and
cloud infrastructure. Requirements: Python, FastAPI, Docker,
Kubernetes. We offer remote-first culture and competitive pay.
Join our small, talented team and build impactful products today.
</main>
<footer>Footer content here</footer>
</body>
</html>
"""


def _make_mock_client(html: str) -> AsyncMock:
    response = MagicMock()
    response.text = html
    response.raise_for_status = MagicMock()
    client = AsyncMock()
    client.get = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client


async def test_scrape_returns_cleaned_text():
    mock_client = _make_mock_client(_JOB_HTML)
    with patch(
        "src.services.scraper.httpx.AsyncClient", return_value=mock_client
    ):
        result = await scrape_job_description("https://example.com/jobs/1")
    assert "Python" in result
    assert "FastAPI" in result
    assert "Navigation links" not in result
    assert "Footer content" not in result


async def test_scrape_uses_os_trust_store():
    mock_client = _make_mock_client(_JOB_HTML)
    with patch(
        "src.services.scraper.httpx.AsyncClient", return_value=mock_client
    ) as mock_ctor:
        await scrape_job_description("https://example.com/jobs/1")
    assert mock_ctor.call_args.kwargs["verify"] is SSL_CONTEXT


async def test_scrape_strips_script_and_style_tags():
    body = "We need a senior Python engineer for backend work. " * 5
    html = (
        "<html><body>"
        "<script>alert('xss')</script>"
        "<style>.cls { color: red; }</style>"
        f"<p>{body}</p>"
        "</body></html>"
    )
    mock_client = _make_mock_client(html)
    with patch(
        "src.services.scraper.httpx.AsyncClient", return_value=mock_client
    ):
        result = await scrape_job_description("https://example.com/jobs/1")
    assert "alert" not in result
    assert "color: red" not in result


async def test_scrape_raises_on_too_short_content():
    mock_client = _make_mock_client("<html><body><p>Hi</p></body></html>")
    with patch(
        "src.services.scraper.httpx.AsyncClient", return_value=mock_client
    ):
        with pytest.raises(ValueError, match="meaningful content"):
            await scrape_job_description("https://example.com/jobs/1")


async def test_scrape_rejects_non_http_scheme():
    with pytest.raises(ValueError, match="http/https"):
        await scrape_job_description("ftp://example.com/jobs/1")


async def test_scrape_rejects_missing_hostname():
    with pytest.raises(ValueError, match="missing hostname"):
        await scrape_job_description("http:///path")


async def test_scrape_rejects_localhost():
    with pytest.raises(ValueError, match="Internal"):
        await scrape_job_description("http://localhost/jobs/1")


async def test_scrape_rejects_private_ip():
    with pytest.raises(ValueError, match="Internal"):
        await scrape_job_description("http://192.168.1.1/jobs/1")


async def test_scrape_raises_on_http_error():
    client = AsyncMock()
    client.get = AsyncMock(
        side_effect=httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=MagicMock(),
        )
    )
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)

    with patch("src.services.scraper.httpx.AsyncClient", return_value=client):
        with pytest.raises(httpx.HTTPStatusError):
            await scrape_job_description("https://example.com/jobs/1")
