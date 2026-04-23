FROM python:3.11-slim-bookworm

WORKDIR /app

# Skip system dependencies - use Python wheels instead

# Copy requirements
COPY services/ml_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
