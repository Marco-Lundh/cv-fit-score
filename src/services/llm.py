import json
from typing import Literal

from groq import AsyncGroq

from src.config import settings
from src.models import FitScoreResponse

_MODEL = "llama-3.3-70b-versatile"

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

_SYSTEM_PROMPT = """\
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
- {language_instruction}
- Respond with ONLY the JSON object, no other text
"""


async def analyze_fit(
    cv_text: str,
    job_description: str,
    language: Literal["en", "sv"] = "en",
) -> FitScoreResponse:
    client = AsyncGroq(api_key=settings.groq_api_key)

    system_prompt = _SYSTEM_PROMPT.format(
        language_instruction=_LANGUAGE_INSTRUCTION[language]
    )

    user_message = (
        f"## CV\n{cv_text}\n\n"
        f"## Job Description\n{job_description}"
    )

    completion = await client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    raw = completion.choices[0].message.content
    data = json.loads(raw)
    return FitScoreResponse(**data)
