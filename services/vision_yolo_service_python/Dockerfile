FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for image processing
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download YOLOv8 model to avoid downloading on first run
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Copy application
COPY main.py .

# Set environment variables
ENV VISION_YOLO_PORT=8005
ENV VISION_YOLO_HOST=0.0.0.0
ENV YOLO_MODEL_PATH=yolov8n.pt

EXPOSE 8005

CMD ["python", "main.py"]
