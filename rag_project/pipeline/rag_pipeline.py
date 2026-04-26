import sys
import time
from rag_project.config.artifact_config import ArtifactConfig
from rag_project.config.settings import pdf_data_path
from rag_project.data_processing.chunk import ChunkProcessor
from rag_project.embeddings.embedding_model import EmbeddingModel
from rag_project.vector_store.pinecone_client import PineconeClient


def print_banner(step: str, index: int, total: int) -> None:
    print("\n" + "=" * 60)
    print(f"  STEP {index}/{total}: {step}")
    print("=" * 60)


def run_pipeline(pdf_path: str) -> None:
    total_steps = 3
    start_time = time.time()

    print("\n" + "=" * 60)
    print("   RAG PIPELINE STARTING")
    print(f"   PDF: {pdf_path}")
    print("=" * 60)

    # ── Shared config ──────────────────────────────────────────────────
    try:
        config = ArtifactConfig(pdf_data_path=pdf_path)
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("Check that your PDF path in rag_project/config/settings.py is correct.")
        sys.exit(1)

    # ── STEP 1: Chunk ──────────────────────────────────────────────────
    print_banner("CHUNKING PDF", 1, total_steps)
    try:
        step1_start = time.time()
        processor = ChunkProcessor(config=config)
        chunks_path = processor.process()
        print(f"[Step 1] ✅ Done in {time.time() - step1_start:.1f}s → {chunks_path}")
    except Exception as e:
        print(f"[Step 1] ❌ Chunking failed: {e}")
        sys.exit(1)

    # ── STEP 2: Embed ──────────────────────────────────────────────────
    print_banner("EMBEDDING CHUNKS", 2, total_steps)
    try:
        step2_start = time.time()
        embedding_model = EmbeddingModel(config=config)
        embeddings_path = embedding_model.process()
        print(f"[Step 2] ✅ Done in {time.time() - step2_start:.1f}s → {embeddings_path}")
    except Exception as e:
        print(f"[Step 2] ❌ Embedding failed: {e}")
        sys.exit(1)

    # ── STEP 3: Upload to Pinecone ─────────────────────────────────────
    print_banner("UPLOADING TO PINECONE", 3, total_steps)
    try:
        step3_start = time.time()
        pinecone_client = PineconeClient(config=config)
        pinecone_client.process()
        print(f"[Step 3] ✅ Done in {time.time() - step3_start:.1f}s")
    except Exception as e:
        print(f"[Step 3] ❌ Pinecone upload failed: {e}")
        sys.exit(1)

    # ── Summary ────────────────────────────────────────────────────────
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"   ✅ PIPELINE COMPLETE in {total_time:.1f}s")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_pipeline(pdf_path=pdf_data_path)

# python -m rag_project.pipeline.rag_pipeline