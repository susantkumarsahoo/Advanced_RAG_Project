from dataclasses import dataclass


@dataclass
class ArtifactDir:
    pdf_chunks_data_path: str
    embaded_chunks_data_path: str
