import os
import pickle
from typing import List

from langchain_core.documents import Document

from rag_project.config.artifact_config import ArtifactConfig
from rag_project.config.artifact_dir import ArtifactDir
from rag_project.config.settings import pdf_data_path
from rag_project.utils.helpers import build_chunked_docs


class ChunkProcessor:
    def __init__(self, config: ArtifactConfig) -> None:
        self.config = config
        # Both fields must be provided — pdf_chunks_data_path was missing before
        self.artifacts_dir = ArtifactDir(
            pdf_chunks_data_path=self.config.pdf_chunks_path,
            embaded_chunks_data_path=self.config.embaded_chunks_path,
        )
        print(f"[ChunkProcessor] Initialized.\n{self.config}")

    def process(self) -> str:
        """Load PDF → clean → chunk → pickle. Returns path to saved file."""
        chunks: List[Document] = build_chunked_docs(self.config.pdf_data_path)

        # artifacts_dir is already created by ArtifactConfig.__init__
        with open(self.artifacts_dir.pdf_chunks_data_path, "wb") as f:
            pickle.dump(chunks, f)

        print(
            f"[ChunkProcessor] Saved {len(chunks)} chunks → "
            f"{self.artifacts_dir.pdf_chunks_data_path}"
        )
        return self.artifacts_dir.pdf_chunks_data_path


if __name__ == "__main__":
    config = ArtifactConfig(pdf_data_path=pdf_data_path)
    processor = ChunkProcessor(config=config)
    processor.process()

# python -m rag_project.data_processing.chunk