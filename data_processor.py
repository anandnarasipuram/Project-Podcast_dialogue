"""
Podcast Studio — data processing step.
Author: Nnanyelugo Ahukannah

Handles the input source. Turns a lesson — a saved file, a public URL, or an
uploaded file (.txt/.md/.pdf) — into cleaned text, and returns a structured
`SourceDocument` that the rest of the pipeline consumes. (Using a dataclass keeps
the data standardized as it flows between modules — one of the project's
requirements.)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceDocument:
    """One unit of input the pipeline knows how to process."""
    title: str
    text: str
    source_type: str
    word_count: int


def _clean(text: str) -> str:
    """Normalise whitespace so the LLM sees tidy input."""
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_transcript(text: str | None = None, file_path: str | None = None,
                    title: str = "Class Recap") -> SourceDocument:
    """Build a SourceDocument from already-loaded text (or a .txt file path).

    The UI-facing loaders (fetch_url_text / read_local_file) hand their text here;
    raises a clear error if nothing usable was provided — the UI turns that into
    a friendly message rather than a crash.
    """
    if file_path:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Transcript file not found: {p}")
        text = p.read_text(encoding="utf-8")

    if not text or not text.strip():
        raise ValueError("No lesson text provided. Pick a saved lesson, use a public URL, or upload a file.")

    cleaned = _clean(text)
    return SourceDocument(
        title=(title or "Class Recap").strip(),
        text=cleaned,
        source_type="text",
        word_count=len(cleaned.split()),
    )


def fetch_url_text(url: str) -> str:
    """Fetch a PUBLIC web page and return its readable text.

    Great for public articles and lesson pages. It CANNOT reach pages behind a
    login (e.g. Ironhack lessons) — those just return a login page — so if we get
    back too little text, we tell the user to upload a file or pick a saved lesson.
    """
    import requests
    from bs4 import BeautifulSoup

    if not url or not url.strip():
        raise ValueError("No URL provided.")
    url = url.strip()

    try:
        resp = requests.get(url, timeout=20,
                            headers={"User-Agent": "Mozilla/5.0 (PodcastStudio)"})
        resp.raise_for_status()
    except Exception as exc:
        raise ValueError(f"Couldn't fetch that URL: {exc}") from exc

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "form", "noscript"]):
        tag.decompose()
    node = soup.find("main") or soup.find("article") or soup.body or soup
    text = _clean(node.get_text("\n", strip=True))

    if len(text.split()) < 40:
        raise ValueError(
            "That page didn't return enough readable text. If it needs a login "
            "(like an Ironhack lesson), upload it as a file or pick a saved lesson instead."
        )
    return text


def read_local_file(path: str) -> str:
    """Read a compatible local file (.txt, .md, or .pdf) and return its text."""
    p = Path(path)
    ext = p.suffix.lower()

    if ext in (".txt", ".md", ".markdown", ".text"):
        text = p.read_text(encoding="utf-8", errors="ignore")
    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError as exc:
            raise ValueError("PDF support needs the 'pypdf' package (pip install pypdf).") from exc
        try:
            reader = PdfReader(str(p))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception as exc:
            raise ValueError(f"Couldn't read that PDF: {exc}") from exc
    else:
        raise ValueError(f"Unsupported file type '{ext or 'unknown'}'. Please use a .txt, .md, or .pdf file.")

    text = _clean(text)
    if len(text.split()) < 5:
        raise ValueError("That file didn't contain readable text. Try a different file.")
    return text
