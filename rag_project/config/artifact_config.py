import os
from rag_project.config.settings import ARTIFACTS_DIR, PDF_CHUNKS_PATH, EMBADED_CHUNKS_PATH


class ArtifactConfig:
    def __init__(self, pdf_data_path: str) -> None:
        if not os.path.exists(pdf_data_path):
            raise FileNotFoundError(f"PDF not found at path: {pdf_data_path}")

        self.pdf_data_path = pdf_data_path

        # Root artifacts directory (absolute, based on cwd)
        self.artifacts_dir = os.path.join(os.getcwd(), ARTIFACTS_DIR)
        os.makedirs(self.artifacts_dir, exist_ok=True)

        # Output file paths (files inside artifacts_dir)
        self.pdf_chunks_path = os.path.join(self.artifacts_dir, PDF_CHUNKS_PATH)
        self.embaded_chunks_path = os.path.join(self.artifacts_dir, EMBADED_CHUNKS_PATH)

    def __repr__(self) -> str:
        return (
            f"ArtifactConfig(\n"
            f"  pdf_data_path={self.pdf_data_path!r},\n"
            f"  artifacts_dir={self.artifacts_dir!r},\n"
            f"  pdf_chunks_path={self.pdf_chunks_path!r},\n"
            f"  embaded_chunks_path={self.embaded_chunks_path!r}\n"
            f")"
        )