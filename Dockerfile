# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for building React
# Node.js 20 — required by Vite 8
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY app/ ./app/
COPY server.py .
COPY frontend/ ./frontend/

# Build React frontend
RUN cd frontend && npm install && npm run build && cd ..

# Create necessary directories
RUN mkdir -p data/chromadb images logs

# Expose port 7860 — Hugging Face uses this port
EXPOSE 7860

# Start FastAPI on port 7860
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]