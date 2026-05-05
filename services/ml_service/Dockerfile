# syntax=docker/dockerfile:1.7
FROM python:3.11-slim-bookworm

WORKDIR /app

# Runtime libs required by cv2 in slim images
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
COPY services/ml_service/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copy source code
COPY services/ml_service/app ./app
COPY services/ml_service/main.py .

# Expose port
EXPOSE 8004

# Health check
HEALTHCHECK --interval=15s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8004/health')" || exit 1

# Run
CMD ["python", "main.py"]
