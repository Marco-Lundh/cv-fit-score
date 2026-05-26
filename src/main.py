import io
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.models import AnalyzeTextRequest, FitScoreResponse
from src.services.llm import analyze_fit
from src.services.pdf import extract_text_from_pdf
from src.services.scraper import scrape_job_description

app = FastAPI(
    title="CV Fit Score",
    description="Analyze how well a CV matches a job description using AI.",
    version="1.0.0",
)

templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post(
    "/analyze/text",
    response_model=FitScoreResponse,
    summary="Analyze CV from plain text",
)
async def analyze_text(body: AnalyzeTextRequest):
    try:
        job_description = await scrape_job_description(body.job_url)
    except Exception as exc:
        raise HTTPException(
            status_code=422, detail=f"Failed to fetch job URL: {exc}"
        ) from exc

    try:
        return await analyze_fit(body.cv_text, job_description, body.language)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"LLM analysis failed: {exc}"
        ) from exc


@app.post(
    "/analyze/pdf",
    response_model=FitScoreResponse,
    summary="Analyze CV from PDF upload",
)
async def analyze_pdf(
    job_url: str = Form(..., description="URL to the job posting"),
    cv_file: UploadFile = File(..., description="CV as a PDF file"),
    language: Literal["en", "sv"] = Form(
        "en", description="Response language"
    ),
):
    if cv_file.content_type != "application/pdf":
        raise HTTPException(
            status_code=422, detail="Only PDF files are accepted."
        )

    file_bytes = await cv_file.read()
    try:
        cv_text = extract_text_from_pdf(io.BytesIO(file_bytes))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        job_description = await scrape_job_description(job_url)
    except Exception as exc:
        raise HTTPException(
            status_code=422, detail=f"Failed to fetch job URL: {exc}"
        ) from exc

    try:
        return await analyze_fit(cv_text, job_description, language)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"LLM analysis failed: {exc}"
        ) from exc


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}
