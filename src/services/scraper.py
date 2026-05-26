import httpx
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
_TIMEOUT = 15.0
_MAX_CHARS = 8000


async def scrape_job_description(url: str) -> str:
    async with httpx.AsyncClient(
        follow_redirects=True, timeout=_TIMEOUT
    ) as client:
        response = await client.get(url, headers=_HEADERS)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result = "\n".join(lines)[:_MAX_CHARS]

    if len(result) < 100:
        raise ValueError(
            "Could not extract meaningful content from the job URL."
        )

    return result
