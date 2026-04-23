FROM python:3.12.3-slim-bookworm

WORKDIR /app

# Skip system dependencies - use Python wheels instead

# Copy requirements
COPY services/vision_service/requirements.txt .

# Install Python dependencies with pre-built wheels (much faster)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/vision_service/app ./app
COPY services/vision_service/main.py .
COPY services/vision_service/models_data ./models_data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8003/health')" || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
