# -----------------------------
# Base Image (lightweight)
# -----------------------------
FROM python:3.10-slim

# -----------------------------
# Environment settings
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------
# System dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Working directory
# -----------------------------
WORKDIR /app

# -----------------------------
# Install Python dependencies
# -----------------------------
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Copy project files
# -----------------------------
COPY . .

# -----------------------------
# Expose ports
# -----------------------------
EXPOSE 8000
EXPOSE 8501

# -----------------------------
# Default command (Backend)
# -----------------------------
CMD ["uvicorn", "rag_project.main:app", "--host", "0.0.0.0", "--port", "8000"]