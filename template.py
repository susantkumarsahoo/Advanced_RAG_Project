import os
from pathlib import Path

# -------------------------
# Project Name
# -------------------------
project_name = "rag_project"

# -------------------------
# Folders
# -------------------------
configs_folder    = "configs"
data_folder       = "data"
artifacts_folder  = "artifacts"
notebooks_folder  = "notebooks"
tests_folder      = "tests"
scripts_folder    = "scripts"
docs_folder       = "docs"
logs_folder       = "logs"

# -------------------------
# File Structure
# -------------------------
list_of_files = [

    # =========================
    # Main Package
    # =========================
    f"{project_name}/__init__.py",

    # -------------------------
    # Config
    # -------------------------
    f"{project_name}/config/__init__.py",
    f"{project_name}/config/config.yaml",
    f"{project_name}/config/settings.py",

    # -------------------------
    # Data Pipeline (RAG Core)
    # -------------------------
    f"{project_name}/data_ingestion/__init__.py",
    f"{project_name}/data_ingestion/loader.py",
    f"{project_name}/data_ingestion/parser.py",

    f"{project_name}/data_processing/__init__.py",
    f"{project_name}/data_processing/cleaner.py",
    f"{project_name}/data_processing/chunker.py",

    # -------------------------
    # Embeddings
    # -------------------------
    f"{project_name}/embeddings/__init__.py",
    f"{project_name}/embeddings/embedding_model.py",

    # -------------------------
    # Vector Store
    # -------------------------
    f"{project_name}/vector_store/__init__.py",
    f"{project_name}/vector_store/pinecone_client.py",

    # -------------------------
    # Retrieval
    # -------------------------
    f"{project_name}/retrieval/__init__.py",
    f"{project_name}/retrieval/retriever.py",
    f"{project_name}/retrieval/reranker.py",

    # -------------------------
    # Prompt & LLM
    # -------------------------
    f"{project_name}/llm/__init__.py",
    f"{project_name}/llm/prompt_template.py",
    f"{project_name}/llm/llm_client.py",

    # -------------------------
    # RAG Pipeline
    # -------------------------
    f"{project_name}/pipeline/__init__.py",
    f"{project_name}/pipeline/rag_pipeline.py",

    # -------------------------
    # Evaluation
    # -------------------------
    f"{project_name}/evaluation/__init__.py",
    f"{project_name}/evaluation/metrics.py",
    f"{project_name}/evaluation/evaluator.py",

    # -------------------------
    # Monitoring
    # -------------------------
    f"{project_name}/monitoring/__init__.py",
    f"{project_name}/monitoring/logger.py",
    f"{project_name}/monitoring/tracking.py",

    # -------------------------
    # API (Keep ONE)
    # -------------------------
    f"{project_name}/api/__init__.py",
    f"{project_name}/api/routes.py",

    # -------------------------
    # Utils (Minimal)
    # -------------------------
    f"{project_name}/utils/__init__.py",
    f"{project_name}/utils/helpers.py",

    # =========================
    # External Folders
    # =========================
    f"{configs_folder}/rag_config.yaml",

    f"{data_folder}/raw/.gitkeep",
    f"{data_folder}/processed/.gitkeep",

    f"{artifacts_folder}/vector_db/.gitkeep",

    f"{notebooks_folder}/experiments.ipynb",

    f"{scripts_folder}/run_pipeline.py",

    f"{tests_folder}/test_pipeline.py",

    f"{docs_folder}/architecture.md",

    f"{logs_folder}/.gitkeep",

    # -------------------------
    # Root Files
    # -------------------------
    "requirements.txt",
    #".env",
    "Dockerfile",
    "docker-compose.yaml",
    "main.py",
]

# -------------------------
# Create Files
# -------------------------
for filepath in list_of_files:
    file_path = Path(filepath)
    os.makedirs(file_path.parent, exist_ok=True)
    
    if not file_path.exists():
        file_path.touch()
        print(f"Created: {file_path}")
    else:
        print(f"Already exists: {file_path}")