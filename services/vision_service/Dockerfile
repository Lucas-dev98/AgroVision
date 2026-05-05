# syntax=docker/dockerfile:1.7
FROM python:3.11-slim-bookworm

WORKDIR /app

# Runtime libs required by OpenCV/ultralytics in slim images
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxcb1 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY services/vision_service/requirements.txt .

# Install Python dependencies with pre-built wheels (much faster)
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copy application code
COPY services/vision_service/app ./app
COPY services/vision_service/main.py .
COPY services/vision_service/models_data ./models_data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8003/health')" || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
