import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models import FitScoreResponse
from src.services.llm import analyze_fit

_MOCK_DATA = {
    "match_score": 78,
    "strengths": ["Python expertise", "FastAPI experience"],
    "weaknesses": ["No k8s experience"],
    "recommendations": ["Learn Kubernetes"],
    "summary": "Strong backend candidate with minor gaps.",
}


def _make_completion(data: dict | None) -> MagicMock:
    completion = MagicMock()
    completion.choices[0].message.content = (
        json.dumps(data) if data is not None else None
    )
    return completion


async def test_analyze_fit_returns_fit_score_response():
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_make_completion(_MOCK_DATA)
    )
    with patch("src.services.llm.AsyncGroq", return_value=mock_client):
        result = await analyze_fit(
            cv_text="Senior Python developer with 5 years experience.",
            job_description="We need a Python/FastAPI backend engineer.",
        )
    assert isinstance(result, FitScoreResponse)
    assert result.match_score == 78
    assert "Python expertise" in result.strengths


async def test_analyze_fit_english_language_instruction():
    mock_client = AsyncMock()
    captured: list[dict] = []

    async def capture(**kwargs):
        captured.extend(kwargs["messages"])
        return _make_completion(_MOCK_DATA)

    mock_client.chat.completions.create = capture
    with patch("src.services.llm.AsyncGroq", return_value=mock_client):
        await analyze_fit(
            cv_text="CV content here.",
            job_description="Job description here.",
            language="en",
        )
    system_content = captured[0]["content"]
    assert "English" in system_content


async def test_analyze_fit_swedish_language_instruction():
    mock_client = AsyncMock()
    captured: list[dict] = []

    async def capture(**kwargs):
        captured.extend(kwargs["messages"])
        return _make_completion(_MOCK_DATA)

    mock_client.chat.completions.create = capture
    with patch("src.services.llm.AsyncGroq", return_value=mock_client):
        await analyze_fit(
            cv_text="CV content here.",
            job_description="Job description here.",
            language="sv",
        )
    system_content = captured[0]["content"]
    assert "svenska" in system_content


async def test_analyze_fit_user_message_includes_cv_and_job():
    mock_client = AsyncMock()
    captured: list[dict] = []

    async def capture(**kwargs):
        captured.extend(kwargs["messages"])
        return _make_completion(_MOCK_DATA)

    mock_client.chat.completions.create = capture
    with patch("src.services.llm.AsyncGroq", return_value=mock_client):
        await analyze_fit(
            cv_text="My unique CV text here.",
            job_description="Unique job description here.",
        )
    user_content = captured[1]["content"]
    assert "My unique CV text here." in user_content
    assert "Unique job description here." in user_content


async def test_analyze_fit_raises_on_empty_response():
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_make_completion(None)
    )
    with patch("src.services.llm.AsyncGroq", return_value=mock_client):
        with pytest.raises(ValueError, match="empty response"):
            await analyze_fit(
                cv_text="CV content here.",
                job_description="Job description here.",
            )
