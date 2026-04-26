import os
import re
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Normalize and clean extracted PDF text."""
    text = re.sub(r"['']", "'", text)                    # smart single quotes
    text = re.sub(r'[""]', '"', text)                    # smart double quotes
    text = re.sub(r"\n\s*\d{1,4}\s*\n", "\n", text)     # lone page numbers
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)         # hyphenated line breaks
    text = re.sub(r"[ \t]+", " ", text)                  # collapse spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)               # collapse blank lines
    return text.strip()


# ---------------------------------------------------------------------------
# PDF loading
# ---------------------------------------------------------------------------

def load_pdf(pdf_path: str) -> List[Document]:
    """
    Load a PDF file and return one Document per page.
    Raises FileNotFoundError if the path does not exist.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    if not pages:
        raise ValueError(f"PyPDFLoader returned 0 pages for: {pdf_path}")

    print(f"[load_pdf] Loaded {len(pages)} pages from: {pdf_path}")
    return pages


# ---------------------------------------------------------------------------
# Chunking pipeline
# ---------------------------------------------------------------------------

def build_chunked_docs(raw_input) -> List[Document]:
    """
    Accept either:
      - a PDF file path (str)  → load with PyPDFLoader
      - a list of Documents   → use directly

    Returns a list of cleaned, chunked Documents ready for embedding.
    """

    # ── STEP 1: Resolve input into List[Document] ──────────────────────────
    if isinstance(raw_input, str):
        # Treat as a file path, not raw text
        if not raw_input.lower().endswith(".pdf"):
            raise ValueError(
                f"String input must be a path to a .pdf file, got: {raw_input!r}"
            )
        docs = load_pdf(raw_input)

    elif (
        isinstance(raw_input, list)
        and len(raw_input) > 0
        and isinstance(raw_input[0], Document)
    ):
        docs = raw_input

    else:
        raise ValueError(
            f"Unsupported input type: {type(raw_input)}. "
            "Pass a PDF file path (str) or List[Document]."
        )

    print(f"[build_chunked_docs] Raw documents received: {len(docs)}")

    # ── STEP 2: Clean and filter short / empty pages ───────────────────────
    cleaned_docs: List[Document] = []
    for doc in docs:
        text = clean_text(doc.page_content)
        if len(text) < 50:          # skip near-empty pages (headers, blanks)
            continue
        cleaned_docs.append(
            Document(
                page_content=text,
                metadata=doc.metadata if hasattr(doc, "metadata") else {},
            )
        )

    if not cleaned_docs:
        raise ValueError(
            "No valid text found after cleaning. "
            "Check that the PDF contains extractable text (not scanned images)."
        )

    print(f"[build_chunked_docs] Valid pages after cleaning: {len(cleaned_docs)}")

    # ── STEP 3: Split into chunks ──────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunked_docs = splitter.split_documents(cleaned_docs)

    if not chunked_docs:
        raise ValueError("Chunking produced 0 chunks. Check chunk_size vs document length.")

    print(f"[build_chunked_docs] Total chunks produced: {len(chunked_docs)}")
    return chunked_docs