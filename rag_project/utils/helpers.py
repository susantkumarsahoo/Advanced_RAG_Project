import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def build_chunked_docs(raw_input):
    # --- Normalize Input ---
    if isinstance(raw_input, str):
        text = raw_input
    elif isinstance(raw_input, list):
        if len(raw_input) > 0 and isinstance(raw_input[0], Document):
            text = "\n".join([doc.page_content for doc in raw_input])
        else:
            text = "\n".join([str(x) for x in raw_input])
    elif isinstance(raw_input, dict):
        text = str(raw_input)
    else:
        raise ValueError(f"Unsupported input type: {type(raw_input)}")

    # --- Clean Text ---
    text = re.sub(r"['']", "'", text)
    text = re.sub(r'[""]', '"', text)
    text = re.sub(r"\n\s*\d{1,4}\s*\n", "\n", text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # --- Remove Noise (repeated lines) ---
    lines = text.split("\n")
    freq = {}
    for line in lines:
        key = line.strip()
        if key:
            freq[key] = freq.get(key, 0) + 1
    text = "\n".join([line for line in lines if freq.get(line.strip(), 0) <= 5])

    # --- Chunk & Return ---
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks_documents = [
        Document(page_content=chunk.strip())
        for chunk in splitter.split_text(text)
        if chunk.strip()
    ]

    return chunks_documents