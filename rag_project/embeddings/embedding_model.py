import os
import pickle
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from rag_project.config.artifact_config import ArtifactConfig
from rag_project.config.artifact_dir import ArtifactDir
from rag_project.config.settings import pdf_data_path
from dotenv import load_dotenv

load_dotenv()

OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"   # 1536-dim, fixed


class EmbeddingModel:
    def __init__(self, config: ArtifactConfig) -> None:
        self.config = config
        self.artifacts_dir = ArtifactDir(
            pdf_chunks_data_path=self.config.pdf_chunks_path,
            embaded_chunks_data_path=self.config.embaded_chunks_path,
        )
        print(f"[EmbeddingModel] Initialized.\n{self.config}")

    def process(self) -> str:
        """
        Load pickled chunks → embed → save (chunk, vector) pairs.
        Returns path to saved embeddings file.
        """
        # Load chunks saved by ChunkProcessor
        with open(self.artifacts_dir.pdf_chunks_data_path, "rb") as f:
            chunks: List[Document] = pickle.load(f)

        if not chunks:
            raise ValueError("Chunk file is empty. Re-run ChunkProcessor first.")

        print(f"[EmbeddingModel] Loaded {len(chunks)} chunks for embedding.")

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found. Check your .env file!")

        embeddings = OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            openai_api_key=openai_api_key,
        )

        texts = [chunk.page_content for chunk in chunks]
        embedded_vectors: List[List[float]] = embeddings.embed_documents(texts)

        print(
            f"[EmbeddingModel] Embedded {len(embedded_vectors)} chunks, "
            f"dim={len(embedded_vectors[0])}"
        )

        # Save (Document, vector) pairs together — Pinecone needs both
        paired: List[Tuple[Document, List[float]]] = list(zip(chunks, embedded_vectors))

        with open(self.artifacts_dir.embaded_chunks_data_path, "wb") as f:
            pickle.dump(paired, f)

        print(
            f"[EmbeddingModel] Saved paired embeddings → "
            f"{self.artifacts_dir.embaded_chunks_data_path}"
        )
        return self.artifacts_dir.embaded_chunks_data_path


if __name__ == "__main__":
    config = ArtifactConfig(pdf_data_path=pdf_data_path)
    model = EmbeddingModel(config=config)
    model.process()

# python -m rag_project.embeddings.embedding_model
