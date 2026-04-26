import os

ARTIFACTS_DIR = 'artifacts'
PDF_CHUNKS_PATH = 'chunk_data.pkl'

# Base directory: goes up three levels from config/settings.py
# settings.py -> config -> rag_project -> Advanced_RAG_Project (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Automatically builds the full path to the PDF file
pdf_data_path = os.path.join(BASE_DIR, "data_from_s3", "SupplyCode.pdf")





# rag_project/config/settings.py
