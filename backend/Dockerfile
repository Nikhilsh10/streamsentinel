FROM python:3.11-slim
WORKDIR /app

# Ensure gcc and other necessary system packages are installed
# Required for building some packages (like confluent-kafka if used)
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Adding extra index URL for torch
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
