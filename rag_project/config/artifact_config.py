import os
from rag_project.config.settings import ARTIFACTS_DIR, PDF_CHUNKS_PATH, pdf_data_path


class ArtifactConfig:
    def __init__(self, pdf_data_path: str) -> None:
        if not os.path.exists(pdf_data_path):
            raise FileNotFoundError(f"PDF not found at path: {pdf_data_path}")

        self.pdf_data_path = pdf_data_path

        # Root artifacts directory
        self.artifacts_dir = os.path.join(os.getcwd(), ARTIFACTS_DIR)
        os.makedirs(self.artifacts_dir, exist_ok=True)  # ✅ only create the folder

        # Chunk output file path (just a path, don't makedirs on this)
        self.pdf_chunks_path = os.path.join(
            self.artifacts_dir,
            PDF_CHUNKS_PATH
        )  # ✅ no makedirs here — chunk_data.pkl is a FILE not a folder
        