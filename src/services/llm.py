import json
from typing import Literal

import httpx
from groq import AsyncGroq

from src.config import get_settings
from src.models import FitScoreResponse
from src.services.tls import SSL_CONTEXT

_MODEL = "llama-3.3-70b-versatile"
_TEMPERATURE = 0.3

_LANGUAGE_INSTRUCTION = {
    "en": (
        "Write all text fields"
        " (strengths, weaknesses, recommendations, summary) in English."
    ),
    "sv": (
        "Skriv alla textfält"
        " (strengths, weaknesses, recommendations, summary) på svenska."
    ),
}


def _build_system_prompt(language: Literal["en", "sv"]) -> str:
    lang_instruction = _LANGUAGE_INSTRUCTION[language]
    return f"""\
You are an expert technical recruiter and career coach.
Analyze the provided CV against the job description and return a JSON
object with exactly these fields:

{{
  "match_score": <integer 0-100>,
  "strengths": [<string>, ...],
  "weaknesses": [<string>, ...],
  "recommendations": [<string>, ...],
  "summary": "<string>"
}}

Rules:
- match_score reflects overall fit (skills, experience, seniority level)
- strengths: 3-5 concrete matching points
- weaknesses: 2-4 genuine gaps — be honest but constructive
- recommendations: 2-4 actionable steps the candidate can take
- summary: 2-3 sentences max
- {lang_instruction}
- Respond with ONLY the JSON object, no other text
"""


async def analyze_fit(
    cv_text: str,
    job_description: str,
    language: Literal["en", "sv"] = "en",
) -> FitScoreResponse:
    system_prompt = _build_system_prompt(language)

    user_message = f"## CV\n{cv_text}\n\n## Job Description\n{job_description}"

    async with httpx.AsyncClient(verify=SSL_CONTEXT) as http_client:
        client = AsyncGroq(
            api_key=get_settings().groq_api_key,
            http_client=http_client,
        )
        completion = await client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=_TEMPERATURE,
        )

    raw = completion.choices[0].message.content
    if raw is None:
        raise ValueError("LLM returned an empty response")
    data = json.loads(raw)
    return FitScoreResponse(**data)
