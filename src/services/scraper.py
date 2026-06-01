import ipaddress
from urllib.parse import urlparse

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
_MINIMUM_CONTENT_LENGTH = 100
_ALLOWED_SCHEMES = frozenset({"http", "https"})


_BLOCKED_HOSTNAMES = frozenset({"localhost"})


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError("Only http/https URLs are accepted.")
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValueError("Invalid URL: missing hostname.")
    if hostname in _BLOCKED_HOSTNAMES:
        raise ValueError("Internal URLs are not allowed.")
    try:
        addr = ipaddress.ip_address(hostname)
    except ValueError:
        return  # hostname is a domain name, not an IP — allow
    if not addr.is_global:
        raise ValueError("Internal URLs are not allowed.")


async def scrape_job_description(url: str) -> str:
    _validate_url(url)
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

    if len(result) < _MINIMUM_CONTENT_LENGTH:
        raise ValueError(
            "Could not extract meaningful content from the job URL."
        )

    return result
