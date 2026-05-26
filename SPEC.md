# CV Fit Score — Project Specification

## Purpose

Portfolio project demonstrating AI integration in a production-grade backend.
Target audience: recruiters and engineers reviewing the GitHub repository.

---

## Functional Requirements

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | HTML form for interactive demo |
| `POST` | `/analyze/text` | Analyze CV submitted as plain text |
| `POST` | `/analyze/pdf` | Analyze CV submitted as a PDF file upload |
| `GET` | `/docs` | Swagger UI (FastAPI built-in) |
| `GET` | `/health` | Health check (used by k8s probes) |

### POST /analyze/text

**Request body (JSON):**
```json
{
  "cv_text": "string (min 50 chars)",
  "job_url": "string (valid URL)"
}
```

**Response:**
```json
{
  "match_score": 78,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "recommendations": ["..."],
  "summary": "..."
}
```

### POST /analyze/pdf

**Request:** `multipart/form-data`
- `job_url` — string (URL to job posting)
- `cv_file` — PDF file (`application/pdf`)

**Response:** same shape as `/analyze/text`

### Response field rules

| Field | Type | Constraints |
|---|---|---|
| `match_score` | integer | 0–100 |
| `strengths` | string[] | 3–5 items |
| `weaknesses` | string[] | 2–4 items |
| `recommendations` | string[] | 2–4 items |
| `summary` | string | 2–3 sentences |

---

## Non-Functional Requirements

- All endpoints respond synchronously (no job queue)
- No authentication required
- No persistence — results are not stored
- Job description scraped live from the provided URL on each request
- PDF text extraction; scanned/image-only PDFs return a 422 error

---

## Error Handling

| Scenario | HTTP status | Detail |
|---|---|---|
| PDF is not `application/pdf` | 422 | "Only PDF files are accepted." |
| PDF contains no extractable text | 422 | "Could not extract text from the PDF…" |
| Job URL unreachable or yields no content | 422 | "Failed to fetch job URL: …" |
| LLM call fails | 500 | "LLM analysis failed: …" |

---

## Tech Stack

| Concern | Technology |
|---|---|
| Language | Python 3.11+ |
| Package management | UV |
| API framework | FastAPI |
| Data validation | Pydantic v2 |
| LLM | Groq — `llama-3.3-70b-versatile` |
| PDF extraction | pdfplumber |
| Web scraping | httpx + BeautifulSoup4 |
| HTML templating | Jinja2 |
| Container | Docker (python:3.12-slim) |
| Orchestration | Kubernetes (Minikube for local) |

---

## Project Structure

```
cv-fit-score/
├── src/
│   ├── main.py              # FastAPI app, routes
│   ├── models.py            # Pydantic schemas
│   ├── services/
│   │   ├── llm.py           # Groq integration
│   │   ├── scraper.py       # Job URL scraping
│   │   └── pdf.py           # PDF text extraction
│   └── templates/
│       └── index.html       # Demo UI
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── secret.yaml
├── Dockerfile
├── .dockerignore
├── .env.example
├── pyproject.toml
├── SPEC.md
└── README.md
```

---

## Infrastructure

### Docker

- Base image: `python:3.12-slim`
- Build tool: `uv pip install --system`
- Exposed port: `8000`
- Entry point: `uvicorn src.main:app --host 0.0.0.0 --port 8000`

### Kubernetes

| Resource | Name | Notes |
|---|---|---|
| Deployment | `cv-fit-score` | 1 replica, `imagePullPolicy: Never` (Minikube) |
| Service | `cv-fit-score` | NodePort 30080 → container 8000 |
| ConfigMap | `cv-fit-score-config` | `APP_ENV=production` |
| Secret | `cv-fit-score-secret` | `GROQ_API_KEY` |

Resource limits per pod: CPU 100m–500m, memory 256Mi–512Mi.
Health probes: readiness on `/health` after 5 s, liveness after 15 s.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key from console.groq.com |

---

## Out of Scope

- User authentication or API keys
- Request/response persistence or history
- Async job queue
- Cloud deployment (AWS, GCP, Azure)
- CV parsing beyond plain text and PDF
- Support for scanned/image-only PDFs
