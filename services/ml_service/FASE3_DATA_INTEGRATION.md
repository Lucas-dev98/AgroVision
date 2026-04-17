# 🚀 FASE 3 - Real Data Integration

**Status**: 🔨 IN PROGRESS
**Date**: 16 de abril de 2026
**Focus**: Loading and preprocessing real cattle data from MongoDB

---

## 📊 What is FASE 3?

FASE 3 transitions from synthetic data to real farm data. This phase involves:

1. **Data Loading** - Extract cattle tracking, behavior, health data from MongoDB
2. **Data Preprocessing** - Validate, normalize, and prepare data for training
3. **Real Datasets** - Create PyTorch datasets from MongoDB collections
4. **Model Fine-tuning** - Train FASE 2 models on actual farm data
5. **Performance Validation** - Measure real-world accuracy and latency

---

## 🎯 Components Implemented

### ✅ 1. Data Loaders (`app/data/loaders.py`)

**TrackingDataLoader**
```python
loader = TrackingDataLoader(db)
trajectories = await loader.get_animal_trajectories(
    animal_id="cow_001",
    start_date=datetime(2026, 3, 1),
    end_date=datetime.utcnow(),
)
```

**BehaviorDataLoader**
```python
loader = BehaviorDataLoader(db)
patterns = await loader.get_animal_behavior_patterns(animal_id="cow_001")
sequences = await loader.get_behavior_sequences(
    animal_id="cow_001",
    behavior_type="grazing",
    min_duration_seconds=10,
)
labeled = await loader.get_labeled_dataset(
    min_samples_per_behavior=10
)
```

**AnomalyDataLoader**
```python
loader = AnomalyDataLoader(db)
baselines = await loader.get_normal_baselines(animal_id="cow_001")
anomalies = await loader.get_annotated_anomalies()
normal, anomaly = await loader.get_anomaly_training_pairs()
```

**ReIDDataLoader**
```python
loader = ReIDDataLoader(db)
images = await loader.get_animal_images_by_camera(
    animal_id="cow_001",
    camera_ids=["cam_001", "cam_002"]
)
pairs = await loader.get_cross_camera_pairs(animal_id="cow_001", positive=True)
dataset = await loader.get_reid_dataset(min_images_per_animal=5)
```

### ✅ 2. Data Preprocessors (`app/data/preprocessors.py`)

**BehaviorPreprocessor**
- Validates behavior records
- Maps behavior types to indices (0-7)
- Normalizes sequences to fixed length
- Extracts temporal features

```python
is_valid, error = BehaviorPreprocessor.validate_behavior_record(record)
normalized_seqs = BehaviorPreprocessor.normalize_sequences(sequences)
features = BehaviorPreprocessor.extract_temporal_features(records)
```

**AnomalyPreprocessor**
- Validates health records
- Normalizes health metrics (z-score)
- Computes anomaly thresholds

```python
normalized, params = AnomalyPreprocessor.normalize_features(records)
scores = AnomalyPreprocessor.compute_anomaly_scores(errors)
```

**ReIDPreprocessor**
- Validates image records and formats
- Creates triplet learning data
- Manages positive/hard negative pairs

```python
triplets = ReIDPreprocessor.prepare_triplets(
    positive_pairs, hard_negatives, max_triplets=1000
)
```

**TemporalPreprocessor**
- Creates sliding windows from sequences
- Pads variable-length sequences
- Normalizes temporal features

```python
windows = TemporalPreprocessor.create_sliding_windows(features, window_size=30)
padded = TemporalPreprocessor.pad_sequences(sequences, target_length=30)
```

### ✅ 3. Real Datasets (`app/data/datasets.py`)

**RealBehaviorDataset** - PyTorch Dataset for CNN training
```python
dataset = RealBehaviorDataset(behavior_records)
frame, label = dataset[0]  # Returns (3, 240, 240) tensor, behavior index
```

**RealAnomalyDataset** - PyTorch Dataset for Autoencoder training
```python
dataset = RealAnomalyDataset(health_records, is_anomaly=False)
features, label = dataset[0]  # Returns (6,) tensor, label (0=normal, 1=anomaly)
```

**RealReIDDataset** - PyTorch Dataset for triplet loss training
```python
dataset = RealReIDDataset(triplets)
anchor, positive, negative = dataset[0]  # Three (3, 224, 224) tensors
```

**RealTemporalDataset** - PyTorch Dataset for LSTM training
```python
dataset = RealTemporalDataset(behavior_sequences)
sequence, label = dataset[0]  # (30, 128) tensor, behavior index
```

**RealDatasetBuilder** - Unified builder for all datasets
```python
builder = RealDatasetBuilder(behavior_loader, anomaly_loader, reid_loader)
behavior_ds = await builder.build_behavior_dataset(min_samples=10)
normal_ds, anomaly_ds = await builder.build_anomaly_dataset()
reid_ds = await builder.build_reid_dataset()
temporal_ds = await builder.build_temporal_dataset()
```

---

## 📁 File Structure

```
services/ml_service/
├── app/data/                              ✅ NEW
│   ├── __init__.py                        ✅ Package init
│   ├── loaders.py                         ✅ 550 LOC - MongoDB loaders
│   ├── preprocessors.py                   ✅ 600 LOC - Data preprocessing
│   └── datasets.py                        ✅ 450 LOC - PyTorch datasets
├── tests/
│   ├── test_data_loaders.py              ✅ NEW - 280 LOC - 20+ tests
│   └── test_integration_fase2.py
└── other files...
```

---

## 🧪 Tests Implemented

**test_data_loaders.py** - 20+ comprehensive tests

✅ **BehaviorPreprocessor** (4 tests)
- Valid record validation
- Invalid record rejection
- Sequence normalization
- Temporal feature extraction

✅ **AnomalyPreprocessor** (3 tests)
- Health record validation
- Feature normalization with z-score
- Anomaly score computation

✅ **ReIDPreprocessor** (2 tests)
- Image record validation
- Triplet preparation

✅ **TemporalPreprocessor** (3 tests)
- Sliding window creation
- Sequence padding
- Feature normalization

✅ **Real Datasets** (8 tests)
- Dataset creation
- Item retrieval
- Tensor shapes
- Label correctness

✅ **Data Loaders** (4 async tests)
- Loader initialization
- Async operations

---

## 🔧 Configuration

### Environment Variables (Required)

```bash
# MongoDB Connection
MONGODB_URL=mongodb://user:pass@localhost:27017
MONGODB_DATABASE=agrovision_ml

# Data Settings
DATA_SYNC_INTERVAL=3600          # Sync data every hour
MIN_SAMPLES_PER_BEHAVIOR=10      # Minimum training samples
MIN_IMAGES_PER_ANIMAL=5          # Re-ID dataset minimum
MAX_TRIPLETS=1000                # Maximum Re-ID triplets
```

### MongoDB Collections Required

```javascript
// tracking collection
db.tracking.insertOne({
    animal_id: "cow_001",
    camera_id: "cam_001",
    position: { x: 100, y: 200 },
    timestamp: new Date(),
    confidence: 0.95
})

// behavior_patterns collection
db.behavior_patterns.insertOne({
    animal_id: "cow_001",
    behavior_type: "grazing",
    timestamp: new Date(),
    duration_seconds: 300,
    confidence: 0.9
})

// animal_health collection
db.animal_health.insertOne({
    animal_id: "cow_001",
    timestamp: new Date(),
    activity_level: 0.7,
    movement_distance: 150,
    heart_rate: 60,
    body_temperature: 38.5,
    feed_consumption: 10,
    water_consumption: 20,
    is_anomaly: false
})

// animal_reid collection
db.animal_reid.insertOne({
    animal_id: "cow_001",
    camera_id: "cam_001",
    image_path: "/storage/images/cow_001_cam_001.jpg",
    timestamp: new Date(),
    quality_score: 0.95
})
```

---

## 📈 Next Steps

### Immediate (Phase 3.1)
- ✅ Create data loaders (DONE)
- ✅ Create preprocessors (DONE)
- ✅ Create real datasets (DONE)
- ⏳ Test data loaders with real MongoDB
- ⏳ Create data sync service

### Short-term (Phase 3.2)
- ⏳ Integrate real data into training pipeline
- ⏳ Modify training scripts to use real datasets
- ⏳ Create data validation dashboard
- ⏳ Implement incremental training

### Medium-term (Phase 3.3)
- ⏳ Fine-tune models on farm data
- ⏳ Validate accuracy on hold-out test set
- ⏳ Optimize for production performance
- ⏳ Create model retraining pipeline

### Long-term (Phase 3.4)
- ⏳ Real-time dashboarding
- ⏳ Edge deployment with fine-tuned models
- ⏳ Continuous learning pipeline
- ⏳ Performance monitoring

---

## 🏃 Quick Start

### 1. Setup Data Infrastructure
```bash
cd /home/lucasbastos/AgroVision/services/ml_service

# Ensure MongoDB is running with agrovision_ml database
docker-compose up -d mongodb

# Create collections with proper indexes
python -m app.data.setup_mongo
```

### 2. Run Tests
```bash
# All data tests
pytest tests/test_data_loaders.py -v

# Specific test class
pytest tests/test_data_loaders.py::TestBehaviorPreprocessor -v

# With coverage
pytest tests/test_data_loaders.py --cov=app.data
```

### 3. Load Real Data
```python
from motor.motor_asyncio import AsyncIOMotorClient
from app.data.loaders import BehaviorDataLoader
from app.data.datasets import RealDatasetBuilder

# Connect to MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.agrovision_ml

# Load data
loader = BehaviorDataLoader(db)
dataset = await loader.get_labeled_dataset(min_samples_per_behavior=10)
```

### 4. Train with Real Data
```bash
# Coming in Phase 3.2
python -m app.training.train \
  --use-real-data \
  --animals cow_001,cow_002,cow_003 \
  --epochs 50 \
  --batch-size 32 \
  --device cuda
```

---

## 📊 Data Statistics

### Expected MongoDB Data Volume

```
Collection          Avg Records    Storage
────────────────────────────────────────
tracking            ~100k/day      ~500MB
behavior_patterns   ~10k/day       ~50MB
animal_health       ~5k/day        ~25MB
animal_reid         ~2k/day        ~1GB (images)
────────────────────────────────────────
Total               ~117k/day      ~1.6GB/day
```

### Training Data Requirements

```
Model               Min Samples    Recommended
────────────────────────────────────
Behavior CNN        ~1000/type     ~10000/type
Anomaly Autoencoder ~500           ~5000
Re-ID ResNet        ~100/animal    ~500/animal
Temporal LSTM       ~200/animal    ~1000/animal
```

---

## 🔍 Monitoring & Debugging

### Check Data Quality
```python
# Validate all behavior records
from app.data.preprocessors import BehaviorPreprocessor

for record in records:
    is_valid, error = BehaviorPreprocessor.validate_behavior_record(record)
    if not is_valid:
        print(f"Invalid record: {error}")
```

### Check Data Distribution
```python
# Get statistics
import numpy as np
behaviors = [r["behavior_type"] for r in records]
unique, counts = np.unique(behaviors, return_counts=True)
print(dict(zip(unique, counts)))
```

### Debug Preprocessing
```python
# Check normalization
normalized, params = AnomalyPreprocessor.normalize_features(records)
print(f"Mean: {np.mean(normalized, axis=0)}")
print(f"Std: {np.std(normalized, axis=0)}")
```

---

## 📞 Support & Issues

**Common Issues:**

1. **MongoDB Connection Error**
   - Ensure MongoDB is running: `docker-compose up -d mongodb`
   - Check connection string in environment variables
   - Verify database `agrovision_ml` exists

2. **No Data Found**
   - Insert sample data: `python -m app.data.seed_mongo`
   - Check animal IDs exist in database
   - Verify timestamp ranges

3. **Memory Errors**
   - Reduce batch size
   - Limit number of records: `limit=5000`
   - Use data streaming instead of loading all at once

4. **Slow Data Loading**
   - Create MongoDB indexes: `db.tracking.createIndex({ animal_id: 1, timestamp: 1 })`
   - Use async operations throughout
   - Consider data partitioning by date

---

## 📚 Documentation

- [FASE2_COMPLETE.md](../FASE2_COMPLETE.md) - FASE 2 Reference
- [README.md](../README.md) - Service Overview
- [MongoDB Collections Guide](../../docs/04_BANCO_DE_DADOS.md)

---

**Status Summary**:
- ✅ Data Loaders: Complete (550 LOC)
- ✅ Preprocessors: Complete (600 LOC)
- ✅ Real Datasets: Complete (450 LOC)
- ✅ Tests: Complete (280+ LOC, 20+ tests)
- ⏳ Integration: In Progress
- ⏳ Fine-tuning: Planned
