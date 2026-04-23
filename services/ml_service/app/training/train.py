"""Training scripts and CLI for ML models"""

import argparse
import json
from pathlib import Path
from typing import Optional, Dict

import torch
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
import torch.nn.functional as F

from app.models.deep_learning import (
    CNNBehaviorClassifier,
    AnomalyDetectionAutoencoder,
    ResNetReID,
    LSTMTemporalAnalyzer,
)
from app.training import (
    BehaviorClassifierTrainer,
    AnomalyDetectorTrainer,
    TemporalAnalyzerTrainer,
)
from app.models.checkpoints import ModelCheckpoint


class TrainingPipeline:
    """Training pipeline for all model types"""

    def __init__(self, checkpoint_dir: str = "models_data", device: str = "cpu"):
        """Initialize training pipeline"""
        self.checkpoint_manager = ModelCheckpoint(checkpoint_dir)
        self.device = device
        self.results = {}

    def generate_synthetic_data(self, num_samples: int = 100, seed: int = 42):
        """Generate synthetic training data for testing"""
        np.random.seed(seed)
        torch.manual_seed(seed)

        print(f"📊 Generating {num_samples} synthetic samples...")

        # Behavior data
        behavior_frames = torch.randn(num_samples, 3, 240, 240)
        behavior_labels = torch.randint(0, 8, (num_samples,))

        # Anomaly data
        anomaly_features = torch.randn(num_samples, 128)
        anomaly_labels = torch.randint(0, 2, (num_samples,))

        # Temporal data
        temporal_sequences = torch.randn(num_samples, 10, 128)
        temporal_labels = torch.randint(0, 8, (num_samples,))

        # ReID data
        reid_frames = torch.randn(num_samples, 3, 224, 224)

        return {
            "behavior": (behavior_frames, behavior_labels),
            "anomaly": (anomaly_features, anomaly_labels),
            "temporal": (temporal_sequences, temporal_labels),
            "reid": reid_frames,
        }

    def train_behavior_model(
        self,
        epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        use_synthetic: bool = True,
    ) -> Dict:
        """Train behavior classifier"""
        print("\n" + "=" * 60)
        print("🧠 Training Behavior Classifier (CNN)")
        print("=" * 60)

        # Generate data
        if use_synthetic:
            data = self.generate_synthetic_data(num_samples=200)
            frames, labels = data["behavior"]
        else:
            raise NotImplementedError("Real data loading not yet implemented")

        # Create model and trainer
        model = CNNBehaviorClassifier(num_classes=8).to(self.device)
        trainer = BehaviorClassifierTrainer(model, device=self.device)

        # Create dataloader
        dataset = TensorDataset(frames, labels)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)

        # Train
        history = trainer.train(
            train_loader=train_loader,
            val_loader=val_loader,
            epochs=epochs,
            learning_rate=learning_rate,
            patience=5,
        )

        # Save best model
        model_path = self.checkpoint_manager.save_model(
            model,
            "behavior_classifier",
            metadata={
                "model_type": "CNN",
                "num_classes": 8,
                "input_size": (3, 240, 240),
                "final_train_loss": float(history["train_loss"][-1]),
                "final_val_loss": float(history["val_loss"][-1]),
                "best_val_loss": float(min(history["val_loss"])),
                "epochs": epochs,
            },
        )

        self.results["behavior"] = {
            "model_path": model_path,
            "history": history,
        }

        # Print results
        print(f"\n✅ Behavior Model Training Complete")
        print(f"   Final train loss: {history['train_loss'][-1]:.4f}")
        print(f"   Best val loss: {min(history['val_loss']):.4f}")
        print(f"   Model saved: {model_path}")

        return history

    def train_anomaly_model(
        self,
        epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        use_synthetic: bool = True,
    ) -> Dict:
        """Train anomaly detection autoencoder"""
        print("\n" + "=" * 60)
        print("🔍 Training Anomaly Detector (Autoencoder)")
        print("=" * 60)

        # Generate data
        if use_synthetic:
            data = self.generate_synthetic_data(num_samples=200)
            features, labels = data["anomaly"]
        else:
            raise NotImplementedError("Real data loading not yet implemented")

        # Create model and trainer
        model = AnomalyDetectionAutoencoder(feature_dim=128, latent_dim=32).to(
            self.device
        )
        trainer = AnomalyDetectorTrainer(model, device=self.device)

        # Create dataloader (only use normal samples for training)
        normal_mask = labels == 0
        normal_features = features[normal_mask]
        dataset = TensorDataset(normal_features)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)

        # Train
        history = trainer.train(
            train_loader=train_loader,
            val_loader=val_loader,
            epochs=epochs,
            learning_rate=learning_rate,
            patience=5,
        )

        # Save model
        model_path = self.checkpoint_manager.save_model(
            model,
            "anomaly_detector",
            metadata={
                "model_type": "Autoencoder",
                "feature_dim": 128,
                "latent_dim": 32,
                "final_train_loss": float(history["train_loss"][-1]),
                "final_val_loss": float(history["val_loss"][-1]),
                "best_val_loss": float(min(history["val_loss"])),
                "epochs": epochs,
            },
        )

        self.results["anomaly"] = {
            "model_path": model_path,
            "history": history,
        }

        # Print results
        print(f"\n✅ Anomaly Model Training Complete")
        print(f"   Final train loss: {history['train_loss'][-1]:.4f}")
        print(f"   Best val loss: {min(history['val_loss']):.4f}")
        print(f"   Model saved: {model_path}")

        return history

    def train_reid_model(
        self,
        epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        use_synthetic: bool = True,
    ) -> Dict:
        """Train Re-ID model"""
        print("\n" + "=" * 60)
        print("🎯 Training Re-ID Model (ResNet)")
        print("=" * 60)

        # Generate data
        if use_synthetic:
            data = self.generate_synthetic_data(num_samples=200)
            frames = data["reid"]
            # Create dummy labels for siamese training
            labels = torch.randint(0, 50, (len(frames),))
        else:
            raise NotImplementedError("Real data loading not yet implemented")

        # Create model
        model = ResNetReID(feature_dim=256).to(self.device)

        # For Re-ID, we typically use triplet loss
        # Simplified: train with classification head
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        train_dataset = TensorDataset(frames, labels)
        train_size = int(0.8 * len(train_dataset))
        val_size = len(train_dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            train_dataset, [train_size, val_size]
        )

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)

        history = {"train_loss": [], "val_loss": []}

        for epoch in range(epochs):
            model.train()
            train_loss = 0.0

            for batch_frames, batch_labels in train_loader:
                batch_frames = batch_frames.to(self.device)
                batch_labels = batch_labels.to(self.device)

                features = model(batch_frames)

                # Simple triplet-like loss: minimize distance between same-id features
                loss = 0.0
                for i in range(len(batch_labels)):
                    for j in range(i + 1, len(batch_labels)):
                        if batch_labels[i] == batch_labels[j]:
                            # Same ID: minimize distance
                            dist = torch.nn.functional.pairwise_distance(
                                features[i:i+1], features[j:j+1]
                            )
                            loss += dist

                if loss > 0:
                    loss = loss / len(batch_labels)
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                train_loss += loss.item() * len(batch_labels)

            train_loss /= len(train_dataset)
            history["train_loss"].append(train_loss)

            # Validation
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_frames, batch_labels in val_loader:
                    batch_frames = batch_frames.to(self.device)
                    batch_labels = batch_labels.to(self.device)

                    features = model(batch_frames)
                    loss = 0.0
                    for i in range(len(batch_labels)):
                        for j in range(i + 1, len(batch_labels)):
                            if batch_labels[i] == batch_labels[j]:
                                dist = torch.nn.functional.pairwise_distance(
                                    features[i:i+1], features[j:j+1]
                                )
                                loss += dist

                    if loss > 0:
                        loss = loss / len(batch_labels)

                    val_loss += loss.item() * len(batch_labels)

            val_loss /= len(val_dataset)
            history["val_loss"].append(val_loss)

            if (epoch + 1) % 2 == 0:
                print(
                    f"Epoch {epoch+1}/{epochs} | Train loss: {train_loss:.4f} | Val loss: {val_loss:.4f}"
                )

        # Save model
        model_path = self.checkpoint_manager.save_model(
            model,
            "reid_model",
            metadata={
                "model_type": "ResNet",
                "feature_dim": 256,
                "input_size": (3, 224, 224),
                "final_train_loss": float(history["train_loss"][-1]),
                "final_val_loss": float(history["val_loss"][-1]),
                "best_val_loss": float(min(history["val_loss"])),
                "epochs": epochs,
            },
        )

        self.results["reid"] = {
            "model_path": model_path,
            "history": history,
        }

        # Print results
        print(f"\n✅ Re-ID Model Training Complete")
        print(f"   Final train loss: {history['train_loss'][-1]:.4f}")
        print(f"   Best val loss: {min(history['val_loss']):.4f}")
        print(f"   Model saved: {model_path}")

        return history

    def train_temporal_model(
        self,
        epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        use_synthetic: bool = True,
    ) -> Dict:
        """Train temporal LSTM model"""
        print("\n" + "=" * 60)
        print("⏱️  Training Temporal Model (LSTM)")
        print("=" * 60)

        # Generate data
        if use_synthetic:
            data = self.generate_synthetic_data(num_samples=200)
            sequences, labels = data["temporal"]
        else:
            raise NotImplementedError("Real data loading not yet implemented")

        # Create model and trainer
        model = LSTMTemporalAnalyzer(input_size=128, hidden_size=256, num_classes=8).to(
            self.device
        )
        trainer = TemporalAnalyzerTrainer(model, device=self.device)

        # Create dataloader
        dataset = TensorDataset(sequences, labels)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)

        # Train
        history = trainer.train(
            train_loader=train_loader,
            val_loader=val_loader,
            epochs=epochs,
            learning_rate=learning_rate,
            patience=5,
        )

        # Save model
        model_path = self.checkpoint_manager.save_model(
            model,
            "temporal_analyzer",
            metadata={
                "model_type": "LSTM",
                "input_size": 128,
                "hidden_size": 256,
                "num_classes": 8,
                "sequence_length": 10,
                "final_train_loss": float(history["train_loss"][-1]),
                "final_val_loss": float(history["val_loss"][-1]),
                "best_val_loss": float(min(history["val_loss"])),
                "epochs": epochs,
            },
        )

        self.results["temporal"] = {
            "model_path": model_path,
            "history": history,
        }

        # Print results
        print(f"\n✅ Temporal Model Training Complete")
        print(f"   Final train loss: {history['train_loss'][-1]:.4f}")
        print(f"   Best val loss: {min(history['val_loss']):.4f}")
        print(f"   Model saved: {model_path}")

        return history

    def train_all_models(
        self,
        epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 0.001,
    ):
        """Train all models"""
        print("\n🚀 Starting FASE 2 Deep Learning Training")
        print(f"   Device: {self.device}")
        print(f"   Epochs: {epochs}")
        print(f"   Batch size: {batch_size}")
        print(f"   Learning rate: {learning_rate}")

        self.train_behavior_model(epochs, batch_size, learning_rate)
        self.train_anomaly_model(epochs, batch_size, learning_rate)
        self.train_reid_model(epochs, batch_size, learning_rate)
        self.train_temporal_model(epochs, batch_size, learning_rate)

        # Print summary
        self.print_summary()

        return self.results

    def print_summary(self):
        """Print training summary"""
        print("\n" + "=" * 60)
        print("📊 Training Summary")
        print("=" * 60)

        for model_name, result in self.results.items():
            print(f"\n{model_name.upper()}:")
            print(f"  Model: {result['model_path']}")
            print(f"  Final train loss: {result['history']['train_loss'][-1]:.4f}")
            print(f"  Best val loss: {min(result['history']['val_loss']):.4f}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Train ML models for cattle analysis")

    parser.add_argument(
        "--model",
        choices=["behavior", "anomaly", "reid", "temporal", "all"],
        default="all",
        help="Model to train",
    )
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument(
        "--learning-rate", type=float, default=0.001, help="Learning rate"
    )
    parser.add_argument(
        "--device", choices=["cpu", "cuda"], default="cpu", help="Device to use"
    )
    parser.add_argument(
        "--checkpoint-dir", default="models_data", help="Checkpoint directory"
    )

    args = parser.parse_args()

    # Create pipeline
    pipeline = TrainingPipeline(
        checkpoint_dir=args.checkpoint_dir,
        device=args.device,
    )

    # Train
    if args.model == "all":
        pipeline.train_all_models(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
        )
    elif args.model == "behavior":
        pipeline.train_behavior_model(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
        )
    elif args.model == "anomaly":
        pipeline.train_anomaly_model(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
        )
    elif args.model == "reid":
        pipeline.train_reid_model(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
        )
    elif args.model == "temporal":
        pipeline.train_temporal_model(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
        )


if __name__ == "__main__":
    main()
