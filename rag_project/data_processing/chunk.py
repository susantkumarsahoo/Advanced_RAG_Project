import os
import pickle
from typing import List

from langchain_core.documents import Document

from rag_project.config.artifact_config import ArtifactConfig
from rag_project.config.settings import pdf_data_path
from rag_project.config.artifact_dir import ArtifactDir
from rag_project.utils.helpers import build_chunked_docs


class ChunkProcessor:
    def __init__(self, config: ArtifactConfig) -> None:
        self.config = config
        self.artifacts_dir = ArtifactDir(
            pdf_chunks_data_path=self.config.pdf_chunks_path
        )

        print(f"ArtifactDir: {self.artifacts_dir}")

    def process(self) -> str:
        chunks: List[Document] = build_chunked_docs(self.config.pdf_data_path)

        # Create the artifacts directory if it doesn't exist
        os.makedirs(os.path.dirname(self.artifacts_dir.pdf_chunks_data_path), exist_ok=True)

        with open(self.artifacts_dir.pdf_chunks_data_path, "wb") as f:
            pickle.dump(chunks, f)

        return self.artifacts_dir.pdf_chunks_data_path

if __name__ == "__main__":
    config = ArtifactConfig(pdf_data_path=pdf_data_path)
    chunk_processor = ChunkProcessor(config=config)
    chunk_processor.process()


# python -m rag_project.data_processing.chunk