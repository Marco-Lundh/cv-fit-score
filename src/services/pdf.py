from typing import BinaryIO

import pdfplumber


def extract_text_from_pdf(file_obj: BinaryIO) -> str:
    with pdfplumber.open(file_obj) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError(
            "Could not extract text from the PDF. Is it scanned/image-only?"
        )
    return text
