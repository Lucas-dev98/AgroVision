# ⚡ FASE 3.2 Quick Start (5 minutes)

## 🚀 Start Real Data Training in 3 Steps

### 1️⃣ Setup MongoDB Data

```bash
cd /home/lucasbastos/AgroVision/services/ml_service

# Seed sample data (FASE 3.1)
python -m app.data.setup_mongo
```

### 2️⃣ Train with Real Data

```bash
# Basic training (50 epochs)
python app/training/train_real_data.py \
    --model behavior \
    --epochs 50 \
    --use-real-data \
    --device cuda

# Or resume from checkpoint
python app/training/train_real_data.py \
    --model behavior \
    --epochs 100 \
    --resume-checkpoint \
    --use-real-data
```

### 3️⃣ Monitor Quality

```bash
# Check data quality
python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.monitoring.data_dashboard import DataQualityDashboard

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['agrovision_ml']
    
    dashboard = DataQualityDashboard(db)
    await dashboard.connect()
    
    report = await dashboard.generate_quality_report()
    print(report)
    
    await dashboard.disconnect()

asyncio.run(main())
"
```

---

## 📋 What's New in Phase 3.2

### Components
- ✅ **Data Sync Service** - Auto sync MongoDB data
- ✅ **Incremental Trainer** - Resume from checkpoints  
- ✅ **Train Script** - `--use-real-data` flag
- ✅ **Dashboard** - Monitor data quality

### Files Created
```
app/data/data_sync.py                    (280 LOC)
app/training/incremental_trainer.py      (380 LOC)
app/training/train_real_data.py          (320 LOC)
app/monitoring/data_dashboard.py         (350 LOC)
tests/test_phase32.py                    (280 LOC)
```

---

## 🎯 Common Commands

```bash
# List available models
python app/training/train_real_data.py --list-models

# Train anomaly detector
python app/training/train_real_data.py \
    --model anomaly \
    --epochs 30 \
    --batch-size 64 \
    --use-real-data

# Train on CPU (no GPU)
python app/training/train_real_data.py \
    --model behavior \
    --device cpu \
    --use-real-data

# Custom learning rate
python app/training/train_real_data.py \
    --model temporal \
    --learning-rate 0.0001 \
    --use-real-data
```

---

## 🔄 Sync Service

```python
from app.data.data_sync import DataSyncService
import asyncio

async def main():
    # Need MongoDB connection
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["agrovision_ml"]
    
    # Create sync service (syncs every 30 min)
    sync = DataSyncService(db, sync_interval_minutes=30)
    
    # Start in background
    await sync.start()
    
    # Check status
    status = await sync.get_sync_status()
    print(f"Running: {status['is_running']}")
    print(f"Collections: {status['collections_monitored']}")
    
    # Stop when done
    await sync.stop()

asyncio.run(main())
```

---

## 📊 Data Dashboard

```python
from app.monitoring.data_dashboard import DataQualityDashboard
import asyncio

async def main():
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["agrovision_ml"]
    
    dashboard = DataQualityDashboard(db)
    await dashboard.connect()
    
    # Generate report
    report = await dashboard.generate_quality_report()
    print(report)
    
    # Check alerts
    alerts = dashboard.check_alerts()
    print(f"Alerts: {len(alerts)}")
    
    # Export metrics
    dashboard.export_metrics("metrics.json")
    
    await dashboard.disconnect()

asyncio.run(main())
```

---

## 📈 Training Loop

```python
from app.training.incremental_trainer import IncrementalTrainer
from app.models.behavior import CNNBehaviorClassifier
import torch

async def main():
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["agrovision_ml"]
    
    # Initialize
    model = CNNBehaviorClassifier()
    trainer = IncrementalTrainer(
        model_path="models/behavior.pt",
        use_real_data=True,
    )
    
    await trainer.initialize_data_managers(db)
    
    # Get data
    train_loader, val_loader, test_loader = await trainer.get_data_loaders(
        batch_size=32,
        data_type="behavior",
    )
    
    # Resume or start fresh
    checkpoint = trainer.load_checkpoint(model)
    start_epoch = trainer.get_start_epoch()
    
    print(f"Starting from epoch {start_epoch}")
    
    # Save training progress
    trainer.save_final_model(model)
    
    await trainer.cleanup()

import asyncio
asyncio.run(main())
```

---

## 🧪 Run Tests

```bash
# All Phase 3.2 tests
pytest tests/test_phase32.py -v

# Specific test
pytest tests/test_phase32.py::TestDataSyncService::test_init -v

# With output
pytest tests/test_phase32.py -vv -s

# Coverage
pytest tests/test_phase32.py --cov=app.data --cov=app.training
```

---

## ✅ Checklist Before Training

- [ ] MongoDB running: `docker-compose up -d mongodb`
- [ ] Data seeded: `python -m app.data.setup_mongo`
- [ ] Checkpoints directory exists: `mkdir -p checkpoints/`
- [ ] Models directory exists: `mkdir -p models/`
- [ ] CUDA available (optional): `python -c "import torch; print(torch.cuda.is_available())"`

---

## 🚨 Troubleshooting

### No data found
```bash
# Seed data first
python -m app.data.setup_mongo

# Verify collections exist
python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['agrovision_ml']
    collections = await db.list_collection_names()
    print('Collections:', collections)

asyncio.run(main())
"
```

### MongoDB not running
```bash
# Start MongoDB
docker-compose up -d mongodb

# Check status
docker-compose ps
```

### Out of memory
```bash
# Reduce batch size
python app/training/train_real_data.py \
    --batch-size 16 \
    --use-real-data

# Or use CPU
python app/training/train_real_data.py \
    --device cpu \
    --use-real-data
```

### Checkpoint not loading
```bash
# Start fresh (ignore checkpoints)
rm -rf checkpoints/behavior/*

python app/training/train_real_data.py \
    --model behavior \
    --use-real-data
```

---

## 📚 Full Documentation

- **Complete Guide**: [FASE3_PHASE32_COMPLETE.md](FASE3_PHASE32_COMPLETE.md)
- **Data Integration**: [FASE3_DATA_INTEGRATION.md](services/ml_service/FASE3_DATA_INTEGRATION.md)
- **Quick Reference**: [FASE3_QUICK_REFERENCE.md](FASE3_QUICK_REFERENCE.md)

---

## 🎯 Next: Phase 3.3

Model fine-tuning on real farm data:

```bash
# Phase 3.3 will include:
# - Fine-tuned behavior classifier
# - Optimized anomaly detection
# - Improved Re-ID accuracy
# - Real-time prediction serving
```

---

## ⏱️ Typical Training Timeline

```
Data Loading:        ~5 min
Epoch 1:             ~15 min
Epochs 2-50:         ~750 min (50 epochs × 15 min)
─────────────────────────────
Total (50 epochs):   ~770 min (~13 hours)

With checkpoints:    Resume in ~5 min + remaining epochs
```

---

**Ready to train? Start with:**
```bash
python app/training/train_real_data.py \
    --model behavior \
    --epochs 50 \
    --use-real-data
```

🚀 **Happy training!**
