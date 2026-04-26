import os
from typing import Generator
import pinecone
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

SYSTEM_PROMPT = """You are a helpful assistant. Answer the user's question 
using ONLY the context provided below. If the answer is not in the context, 
say "I don't have enough information to answer that."

Context:
{context}"""


def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def search_vectors(query: str, top_k: int = 5) -> str:
    vector = get_embedding(query)
    results = index.query(vector=vector, top_k=top_k, include_metadata=True)
    
    chunks = [
        match.metadata.get("text", "")
        for match in results.matches
        if match.metadata.get("text")
    ]
    return "\n\n".join(chunks)


def stream_answer(query: str) -> Generator[str, None, None]:
    context = search_vectors(query)
    
    if not context:
        yield "No relevant context found in the document."
        return

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": query},
        ],
        stream=True,
        temperature=0.2,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta