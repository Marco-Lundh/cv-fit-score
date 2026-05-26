import pytest
from pydantic import ValidationError

from src.models import AnalyzeTextRequest, FitScoreResponse


def test_analyze_text_request_valid():
    req = AnalyzeTextRequest(
        cv_text="a" * 50,
        job_url="https://example.com/jobs/1",
        language="en",
    )
    assert req.language == "en"


def test_analyze_text_request_cv_too_short():
    with pytest.raises(ValidationError):
        AnalyzeTextRequest(
            cv_text="short",
            job_url="https://example.com/jobs/1",
            language="en",
        )


def test_analyze_text_request_swedish_language():
    req = AnalyzeTextRequest(
        cv_text="a" * 50,
        job_url="https://example.com/jobs/1",
        language="sv",
    )
    assert req.language == "sv"


def test_analyze_text_request_invalid_language():
    with pytest.raises(ValidationError):
        AnalyzeTextRequest(
            cv_text="a" * 50,
            job_url="https://example.com/jobs/1",
            language="fr",  # type: ignore[arg-type]
        )


def test_fit_score_response_valid():
    resp = FitScoreResponse(
        match_score=75,
        strengths=["Python", "FastAPI"],
        weaknesses=["No k8s experience"],
        recommendations=["Learn k8s"],
        summary="Good fit overall.",
    )
    assert resp.match_score == 75


def test_fit_score_response_score_above_100():
    with pytest.raises(ValidationError):
        FitScoreResponse(
            match_score=150,
            strengths=[],
            weaknesses=[],
            recommendations=[],
            summary="",
        )


def test_fit_score_response_score_below_0():
    with pytest.raises(ValidationError):
        FitScoreResponse(
            match_score=-1,
            strengths=[],
            weaknesses=[],
            recommendations=[],
            summary="",
        )
