# rag_project/config/artifact_config.py

import os
from rag_project.config.settings import ARTIFACTS_DIR, PDF_CHUNKS_PATH


class ArtifactConfig:
    def __init__(self, pdf_data_path: str) -> None:
        # ✅ FIX: Validate that the PDF file actually exists at startup
        if not os.path.exists(pdf_data_path):
            raise FileNotFoundError(f"PDF not found at path: {pdf_data_path}")

        self.pdf_data_path = pdf_data_path

        # Root artifacts directory
        self.artifacts_dir = os.path.join(os.getcwd(), ARTIFACTS_DIR)
        os.makedirs(self.artifacts_dir, exist_ok=True)

        # Chunk output directory
        self.pdf_chunks_path = os.path.join(
            self.artifacts_dir,
            PDF_CHUNKS_PATH
        )
        os.makedirs(self.pdf_chunks_path, exist_ok=True)