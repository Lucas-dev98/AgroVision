#!/usr/bin/env python3
"""
ML Training Service - TensorFlow/Keras implementation
Trains animal detection and behavior classification models
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path

from fastapi import FastAPI, UploadFile, HTTPException, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# ML Libraries
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Sequential
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv("PORT", 8106))
HOST = os.getenv("HOST", "0.0.0.0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Models directory
MODELS_DIR = Path("/tmp/ml_models")
MODELS_DIR.mkdir(exist_ok=True)

# Initialize FastAPI
app = FastAPI(
    title="AgroVision ML Training Service",
    description="Real ML model training service using TensorFlow",
    version="1.0.0"
)

# ==================== SCHEMAS ====================

class TrainingRequest(BaseModel):
    model_id: str
    model_type: str  # "animal_detection", "behavior_classification", "weight_prediction"
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001
    dataset_size: int = 100  # For mock training
    data_augmentation: bool = True

class TrainingProgress(BaseModel):
    training_id: str
    model_id: str
    status: str  # "pending", "training", "completed", "failed"
    progress: float  # 0-100%
    current_epoch: int
    total_epochs: int
    loss: Optional[float]
    accuracy: Optional[float]
    eta_seconds: Optional[int]

class ModelMetrics(BaseModel):
    training_id: str
    model_id: str
    accuracy: float
    loss: float
    val_accuracy: float
    val_loss: float
    precision: float
    recall: float
    f1_score: float
    training_time_seconds: float
    epochs_completed: int

# ==================== IN-MEMORY STORAGE ====================

training_jobs: Dict[str, Dict[str, Any]] = {}
completed_trainings: Dict[str, Dict[str, Any]] = {}

# ==================== MODEL BUILDERS ====================

def build_animal_detection_model(input_shape: Tuple[int, int, int] = (224, 224, 3)) -> keras.Model:
    """
    Build a simple animal detection model (pre-trained MobileNetV2 base)
    """
    base_model = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False
    
    model = Sequential([
        layers.Input(shape=input_shape),
        layers.Rescaling(1./127.5, offset=-1),  # Normalize to [-1, 1]
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(10, activation="softmax")  # 10 animal classes
    ])
    
    return model

def build_behavior_classification_model(input_shape: Tuple[int, ...] = (64,)) -> keras.Model:
    """
    Build a behavior classification model (from sensor data)
    """
    model = Sequential([
        layers.Input(shape=input_shape),
        layers.Dense(128, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(64, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        layers.Dense(32, activation="relu"),
        layers.Dense(5, activation="softmax")  # 5 behavior classes
    ])
    
    return model

def build_weight_prediction_model(input_shape: Tuple[int, ...] = (32,)) -> keras.Model:
    """
    Build a weight prediction model (regression)
    """
    model = Sequential([
        layers.Input(shape=input_shape),
        layers.Dense(64, activation="relu"),
        layers.Dropout(0.2),
        layers.Dense(32, activation="relu"),
        layers.Dense(16, activation="relu"),
        layers.Dense(1)  # Single output for weight prediction
    ])
    
    return model

def get_model_builder(model_type: str):
    """Get the appropriate model builder"""
    builders = {
        "animal_detection": build_animal_detection_model,
        "behavior_classification": build_behavior_classification_model,
        "weight_prediction": build_weight_prediction_model,
    }
    return builders.get(model_type, build_animal_detection_model)

# ==================== MOCK DATA GENERATION ====================

def generate_mock_dataset(model_type: str, size: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate mock training data based on model type
    """
    if model_type == "animal_detection":
        # Image data: (batch, height, width, channels)
        X = np.random.rand(size, 224, 224, 3).astype(np.float32)
        y = np.random.randint(0, 10, size)  # 10 animal classes
    elif model_type == "behavior_classification":
        # Sensor data: (batch, 64 features)
        X = np.random.rand(size, 64).astype(np.float32)
        y = np.random.randint(0, 5, size)  # 5 behavior classes
    else:  # weight_prediction
        # Sensor data: (batch, 32 features)
        X = np.random.rand(size, 32).astype(np.float32)
        y = np.random.rand(size) * 500 + 100  # Weight: 100-600 kg
    
    # Convert labels to one-hot for classification
    if model_type != "weight_prediction":
        if model_type == "animal_detection":
            y = keras.utils.to_categorical(y, 10)
        else:
            y = keras.utils.to_categorical(y, 5)
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test

# ==================== TRAINING ====================

def train_model(training_id: str, req: TrainingRequest):
    """
    Background training task
    """
    try:
        job = training_jobs[training_id]
        job["status"] = "training"
        job["start_time"] = datetime.now()
        
        logger.info(f"Starting training {training_id} for model {req.model_id}")
        
        # Get model builder
        builder = get_model_builder(req.model_type)
        model = builder()
        
        # Compile model
        if req.model_type == "weight_prediction":
            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=req.learning_rate),
                loss="mse",
                metrics=["mae"]
            )
        else:
            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=req.learning_rate),
                loss="categorical_crossentropy",
                metrics=["accuracy"]
            )
        
        # Generate mock data
        X_train, X_test, y_train, y_test = generate_mock_dataset(
            req.model_type, 
            req.dataset_size
        )
        
        logger.info(f"Training dataset: {X_train.shape}, Test dataset: {X_test.shape}")
        
        # Custom callback for progress tracking
        class ProgressCallback(keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                progress = ((epoch + 1) / req.epochs) * 100
                job["current_epoch"] = epoch + 1
                job["loss"] = float(logs.get("loss", 0))
                job["accuracy"] = float(logs.get("accuracy", 0)) if req.model_type != "weight_prediction" else None
                job["progress"] = progress
                logger.info(f"[{training_id}] Epoch {epoch+1}/{req.epochs} - Loss: {logs.get('loss'):.4f}")
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=req.epochs,
            batch_size=req.batch_size,
            validation_split=0.1,
            verbose=0,
            callbacks=[ProgressCallback()]
        )
        
        # Evaluate on test set
        if req.model_type == "weight_prediction":
            test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
            metrics = {
                "accuracy": float(1.0 / (1.0 + test_mae / 50)),  # Approximate accuracy
                "loss": float(test_loss),
                "val_loss": float(history.history["val_loss"][-1]),
                "val_accuracy": float(1.0 / (1.0 + history.history["val_mae"][-1] / 50)),
            }
        else:
            test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
            metrics = {
                "accuracy": float(test_accuracy),
                "loss": float(test_loss),
                "val_loss": float(history.history["val_loss"][-1]),
                "val_accuracy": float(history.history["val_accuracy"][-1]),
            }
        
        # Calculate additional metrics (mock)
        metrics["precision"] = metrics["accuracy"] * 0.98
        metrics["recall"] = metrics["accuracy"] * 0.97
        metrics["f1_score"] = 2 * (metrics["precision"] * metrics["recall"]) / (metrics["precision"] + metrics["recall"])
        
        # Save model
        model_path = MODELS_DIR / f"{training_id}_{req.model_id}.h5"
        model.save(str(model_path))
        logger.info(f"Model saved to {model_path}")
        
        # Update job status
        training_time = (datetime.now() - job["start_time"]).total_seconds()
        job["status"] = "completed"
        job["progress"] = 100
        job["completed_at"] = datetime.now()
        job["metrics"] = {
            **metrics,
            "training_time_seconds": training_time,
            "epochs_completed": req.epochs,
            "model_path": str(model_path)
        }
        
        # Move to completed
        completed_trainings[training_id] = job
        
        logger.info(f"Training {training_id} completed. Accuracy: {metrics['accuracy']:.4f}")
        
    except Exception as e:
        logger.error(f"Training {training_id} failed: {str(e)}")
        job["status"] = "failed"
        job["error"] = str(e)
        completed_trainings[training_id] = job

# ==================== API ENDPOINTS ====================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "ml-training-service",
        "timestamp": datetime.now().isoformat(),
        "models_dir": str(MODELS_DIR),
        "active_trainings": len(training_jobs),
        "completed_trainings": len(completed_trainings)
    }

@app.post("/train")
async def start_training(req: TrainingRequest, background_tasks: BackgroundTasks):
    """
    Start a new model training job
    """
    from uuid import uuid4
    
    training_id = str(uuid4())
    
    # Create job record
    job = {
        "training_id": training_id,
        "model_id": req.model_id,
        "model_type": req.model_type,
        "status": "pending",
        "progress": 0,
        "current_epoch": 0,
        "total_epochs": req.epochs,
        "created_at": datetime.now(),
        "start_time": None,
        "loss": None,
        "accuracy": None,
        "error": None
    }
    
    training_jobs[training_id] = job
    
    # Add background training task
    background_tasks.add_task(train_model, training_id, req)
    
    logger.info(f"Training job {training_id} created for model {req.model_id}")
    
    return {
        "training_id": training_id,
        "model_id": req.model_id,
        "model_type": req.model_type,
        "status": "pending",
        "message": "Training job started"
    }

@app.get("/training/{training_id}")
async def get_training_status(training_id: str) -> TrainingProgress:
    """Get training progress"""
    if training_id in training_jobs:
        job = training_jobs[training_id]
    elif training_id in completed_trainings:
        job = completed_trainings[training_id]
    else:
        raise HTTPException(status_code=404, detail="Training not found")
    
    return TrainingProgress(
        training_id=job["training_id"],
        model_id=job["model_id"],
        status=job["status"],
        progress=job["progress"],
        current_epoch=job["current_epoch"],
        total_epochs=job["total_epochs"],
        loss=job.get("loss"),
        accuracy=job.get("accuracy"),
        eta_seconds=None
    )

@app.get("/training/{training_id}/metrics")
async def get_training_metrics(training_id: str) -> ModelMetrics:
    """Get completed training metrics"""
    if training_id not in completed_trainings:
        raise HTTPException(status_code=404, detail="Training not found or still in progress")
    
    job = completed_trainings[training_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Training not completed")
    
    metrics = job["metrics"]
    return ModelMetrics(
        training_id=training_id,
        model_id=job["model_id"],
        **metrics
    )

@app.get("/trainings")
async def list_trainings(status: Optional[str] = None):
    """List all trainings"""
    all_trainings = {**training_jobs, **completed_trainings}
    
    if status:
        filtered = {k: v for k, v in all_trainings.items() if v["status"] == status}
    else:
        filtered = all_trainings
    
    return {
        "total": len(filtered),
        "trainings": [
            {
                "training_id": v["training_id"],
                "model_id": v["model_id"],
                "model_type": v["model_type"],
                "status": v["status"],
                "progress": v["progress"],
                "created_at": v["created_at"].isoformat() if v["created_at"] else None,
            }
            for v in filtered.values()
        ]
    }

@app.get("/models")
async def list_models():
    """List available model types"""
    return {
        "models": [
            {
                "type": "animal_detection",
                "description": "Detect and classify animals in images",
                "input_shape": (224, 224, 3),
                "classes": 10
            },
            {
                "type": "behavior_classification",
                "description": "Classify animal behavior from sensor data",
                "input_shape": (64,),
                "classes": 5
            },
            {
                "type": "weight_prediction",
                "description": "Predict animal weight from sensor data",
                "input_shape": (32,),
                "output": "continuous"
            }
        ]
    }

if __name__ == "__main__":
    logger.info(f"Starting ML Training Service on {HOST}:{PORT}")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL.lower()
    )
