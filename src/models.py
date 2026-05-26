from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeTextRequest(BaseModel):
    cv_text: str = Field(
        ..., min_length=50, description="Full CV content as plain text"
    )
    job_url: str = Field(..., description="URL to the job posting")
    language: Literal["en", "sv"] = Field(
        "en", description="Response language: 'en' or 'sv'"
    )


class FitScoreResponse(BaseModel):
    match_score: int = Field(..., ge=0, le=100, description="Overall fit score 0–100")
    strengths: list[str] = Field(..., description="Key matching strengths")
    weaknesses: list[str] = Field(..., description="Gaps or missing qualifications")
    recommendations: list[str] = Field(
        ..., description="Actionable steps to improve fit"
    )
    summary: str = Field(..., description="Short overall assessment")
