# rag_project/utils/helpers.py

from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def build_chunked_docs(
    pdf_data_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    """
    Load a PDF and split it into overlapping text chunks.

    Args:
        pdf_data_path:  Absolute path to the PDF file.
        chunk_size:     Maximum characters per chunk.
        chunk_overlap:  Characters of overlap between consecutive chunks.

    Returns:
        List of LangChain Document objects.
    """

    # ✅ Step 1: Load PDF pages
    loader = PyPDFLoader(pdf_data_path)
    pages: List[Document] = loader.load()

    if not pages:
        raise ValueError(f"No content loaded from PDF: {pdf_data_path}")

    print(f"[INFO] Loaded {len(pages)} page(s) from PDF.")

    # ✅ Step 2: Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks: List[Document] = splitter.split_documents(pages)

    print(f"[INFO] Split into {len(chunks)} chunk(s).")

    return chunks