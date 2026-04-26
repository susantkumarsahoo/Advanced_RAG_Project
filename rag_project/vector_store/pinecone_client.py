import os
import pickle
import time
from typing import List, Tuple

from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec

from rag_project.config.artifact_config import ArtifactConfig
from rag_project.config.artifact_dir import ArtifactDir
from rag_project.config.settings import pdf_data_path
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
EXPECTED_DIMENSION = 1536       # text-embedding-ada-002 fixed output dim
UPSERT_BATCH_SIZE = 100         # Pinecone recommends ≤ 100 vectors per upsert
INDEX_READY_POLL_SECONDS = 2    # how long to wait between readiness checks


class PineconeClient:
    def __init__(self, config: ArtifactConfig) -> None:
        self.config = config
        self.artifacts_dir = ArtifactDir(
            pdf_chunks_data_path=self.config.pdf_chunks_path,
            embaded_chunks_data_path=self.config.embaded_chunks_path,
        )

        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not found. Check your .env file!")
        if not PINECONE_INDEX_NAME:
            raise ValueError("PINECONE_INDEX_NAME not found. Check your .env file!")

        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index_name = PINECONE_INDEX_NAME
        print(f"[PineconeClient] Initialized. Target index: {self.index_name!r}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _wait_for_index_ready(self) -> None:
        """Poll until the Pinecone index reports ready status."""
        print(f"[PineconeClient] Waiting for index '{self.index_name}' to be ready...")
        while True:
            status = self.pc.describe_index(self.index_name).status
            if status.get("ready"):
                print(f"[PineconeClient] Index is ready.")
                break
            time.sleep(INDEX_READY_POLL_SECONDS)

    def _ensure_index(self, dimension: int) -> None:
        """Create the index if it does not exist; validate dimension if it does."""
        existing = self.pc.list_indexes().names()

        if self.index_name not in existing:
            print(
                f"[PineconeClient] Creating index '{self.index_name}' "
                f"with dim={dimension}, metric=cosine ..."
            )
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            self._wait_for_index_ready()
        else:
            # Validate that the existing index has the correct dimension
            info = self.pc.describe_index(self.index_name)
            existing_dim = info.dimension
            if existing_dim != dimension:
                raise ValueError(
                    f"Dimension mismatch: index '{self.index_name}' has dim={existing_dim}, "
                    f"but embeddings have dim={dimension}. "
                    "Delete the index in the Pinecone console and re-run."
                )
            print(
                f"[PineconeClient] Index '{self.index_name}' already exists "
                f"with dim={existing_dim}. Skipping creation."
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self):
        """
        Load (Document, vector) pairs → validate → upsert to Pinecone in batches.
        Returns the live Pinecone Index object.
        """
        # ── Load embeddings ────────────────────────────────────────────
        with open(self.artifacts_dir.embaded_chunks_data_path, "rb") as f:
            paired: List[Tuple[Document, List[float]]] = pickle.load(f)

        if not paired:
            raise ValueError("Embeddings file is empty. Re-run EmbeddingModel first.")

        chunks, embedded_vectors = zip(*paired)  # unzip into two tuples

        # ── Validate embedding dimension ───────────────────────────────
        actual_dim = len(embedded_vectors[0])
        if actual_dim != EXPECTED_DIMENSION:
            raise ValueError(
                f"Embedding dimension mismatch: expected {EXPECTED_DIMENSION}, "
                f"got {actual_dim}. Re-run EmbeddingModel or update EXPECTED_DIMENSION."
            )

        # ── Ensure index exists and is ready ───────────────────────────
        self._ensure_index(dimension=actual_dim)
        index = self.pc.Index(self.index_name)

        # ── Build vector records with metadata ─────────────────────────
        # Pinecone record format: (id, values, metadata)
        vectors = [
            (
                str(i),
                list(embedded_vectors[i]),
                {
                    "text": chunks[i].page_content,
                    **chunks[i].metadata,          # source, page number, etc.
                },
            )
            for i in range(len(embedded_vectors))
        ]

        # ── Upsert in batches ──────────────────────────────────────────
        total_batches = (len(vectors) + UPSERT_BATCH_SIZE - 1) // UPSERT_BATCH_SIZE
        for batch_idx in range(total_batches):
            start = batch_idx * UPSERT_BATCH_SIZE
            batch = vectors[start : start + UPSERT_BATCH_SIZE]
            index.upsert(vectors=batch)
            print(
                f"[PineconeClient] Upserted batch {batch_idx + 1}/{total_batches} "
                f"({len(batch)} vectors)"
            )

        print(
            f"[PineconeClient] ✅ Done. {len(vectors)} vectors stored in "
            f"index '{self.index_name}'."
        )
        return index


if __name__ == "__main__":
    config = ArtifactConfig(pdf_data_path=pdf_data_path)
    client = PineconeClient(config=config)
    client.process()

# python -m rag_project.vector_store.pinecone_client

