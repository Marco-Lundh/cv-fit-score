import io
from unittest.mock import MagicMock, patch

import pytest

from src.services.pdf import extract_text_from_pdf


def _make_mock_pdf(pages_text: list[str]) -> MagicMock:
    pages = []
    for text in pages_text:
        page = MagicMock()
        page.extract_text.return_value = text
        pages.append(page)
    mock_pdf = MagicMock()
    mock_pdf.pages = pages
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    return mock_pdf


def test_extract_text_returns_content():
    mock_pdf = _make_mock_pdf(["John Doe\nSoftware Engineer"])
    with patch("src.services.pdf.pdfplumber.open", return_value=mock_pdf):
        result = extract_text_from_pdf(io.BytesIO(b"fake"))
    assert "John Doe" in result
    assert "Software Engineer" in result


def test_extract_text_joins_multiple_pages():
    mock_pdf = _make_mock_pdf(["Page one content", "Page two content"])
    with patch("src.services.pdf.pdfplumber.open", return_value=mock_pdf):
        result = extract_text_from_pdf(io.BytesIO(b"fake"))
    assert "Page one content" in result
    assert "Page two content" in result


def test_extract_text_raises_on_empty_pdf():
    mock_pdf = _make_mock_pdf([""])
    with patch("src.services.pdf.pdfplumber.open", return_value=mock_pdf):
        with pytest.raises(ValueError, match="scanned"):
            extract_text_from_pdf(io.BytesIO(b"fake"))


def test_extract_text_raises_when_all_pages_empty():
    mock_pdf = _make_mock_pdf(["", "", ""])
    with patch("src.services.pdf.pdfplumber.open", return_value=mock_pdf):
        with pytest.raises(ValueError):
            extract_text_from_pdf(io.BytesIO(b"fake"))
