# MongoDB Persistence Integration - Phase 6 (In Progress)

## 🎯 Objetivo

Implementar camada de persistência MongoDB para armazenar:
1. **Vision Detections** - Resultados de detecção YOLO
2. **ML Training History** - Histórico de treinamento de modelos
3. **ML Predictions** - Histórico de predições

## 📋 Escopo de Trabalho

### 1. MongoDB Collections Schema

**Collection: `vision_detections`**
```json
{
  "_id": ObjectId,
  "id": "detect_1715001234.567",
  "image_url": "s3://bucket/images/photo.jpg",
  "detections": [
    {
      "class": "cow",
      "confidence": 0.9234,
      "bbox": [125.43, 156.78, 298.56, 445.32]
    }
  ],
  "model_used": "yolov8n",
  "image_hash": "sha256...",
  "image_size_kb": 245.6,
  "processing_time_ms": 125,
  "user_id": "user123",
  "animal_id": "animal456",  // Optional: link to animal
  "created_at": ISODate("2026-05-05T14:30:45.123Z"),
  "updated_at": ISODate("2026-05-05T14:30:45.123Z"),
  "deleted_at": null
}
```

**Collection: `ml_training_history`**
```json
{
  "_id": ObjectId,
  "id": "train_1715001234.567",
  "model_id": "model_1",
  "model_name": "Detecção de Anomalias",
  "status": "completed",  // pending, training, completed, failed
  "parameters": {
    "epochs": 50,
    "batch_size": 32,
    "learning_rate": 0.001,
    "dataset_size": 1000
  },
  "metrics": {
    "accuracy": 0.9456,
    "loss": 0.1234,
    "val_accuracy": 0.9234,
    "val_loss": 0.1456
  },
  "duration_seconds": 3600,
  "training_framework": "tensorflow",  // tensorflow, pytorch, sklearn
  "dataset_id": "dataset_v2",
  "data_augmentation": true,
  "user_id": "user123",
  "notes": "Training with 2024 data",
  "started_at": ISODate("2026-05-05T10:00:00.000Z"),
  "completed_at": ISODate("2026-05-05T11:00:00.000Z"),
  "error_message": null,
  "created_at": ISODate("2026-05-05T10:00:00.000Z"),
  "updated_at": ISODate("2026-05-05T11:00:00.000Z")
}
```

**Collection: `ml_predictions`**
```json
{
  "_id": ObjectId,
  "id": "pred_1715001234.567",
  "model_id": "model_1",
  "model_name": "Detecção de Anomalias",
  "input": {
    "type": "image",
    "url": "s3://bucket/images/test.jpg",
    "features": [0.45, 0.67, 0.23, ...]
  },
  "output": {
    "prediction": "anomaly_detected",
    "confidence": 0.8754,
    "probabilities": {
      "normal": 0.1246,
      "anomaly": 0.8754
    }
  },
  "processing_time_ms": 245,
  "user_id": "user123",
  "animal_id": "animal456",  // Optional: link to animal
  "created_at": ISODate("2026-05-05T14:30:45.123Z"),
  "updated_at": ISODate("2026-05-05T14:30:45.123Z")
}
```

### 2. Indices MongoDB

```javascript
// vision_detections
db.vision_detections.createIndex({ user_id: 1, created_at: -1 })
db.vision_detections.createIndex({ animal_id: 1, created_at: -1 })
db.vision_detections.createIndex({ image_hash: 1 })
db.vision_detections.createIndex({ model_used: 1 })
db.vision_detections.createIndex({ "detections.class": 1 })

// ml_training_history
db.ml_training_history.createIndex({ model_id: 1, created_at: -1 })
db.ml_training_history.createIndex({ user_id: 1, created_at: -1 })
db.ml_training_history.createIndex({ status: 1 })
db.ml_training_history.createIndex({ started_at: 1 })

// ml_predictions
db.ml_predictions.createIndex({ model_id: 1, created_at: -1 })
db.ml_predictions.createIndex({ user_id: 1, created_at: -1 })
db.ml_predictions.createIndex({ animal_id: 1 })
db.ml_predictions.createIndex({ created_at: -1 })
```

### 3. Go MongoDB Layers

**File: `services/vision_service_go/internal/db/mongo.go`**
```go
package db

import (
	"context"
	"time"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type MongoConnection struct {
	Client   *mongo.Client
	Database *mongo.Database
}

type VisionDetection struct {
	ID              string      `bson:"_id,omitempty" json:"id"`
	ImageURL        string      `bson:"image_url" json:"image_url"`
	Detections      []Detection `bson:"detections" json:"detections"`
	ModelUsed       string      `bson:"model_used" json:"model_used"`
	ImageHash       string      `bson:"image_hash" json:"image_hash"`
	ImageSizeKB     float64     `bson:"image_size_kb" json:"image_size_kb"`
	ProcessingTimeMS int        `bson:"processing_time_ms" json:"processing_time_ms"`
	UserID          string      `bson:"user_id" json:"user_id"`
	AnimalID        string      `bson:"animal_id" json:"animal_id"`
	CreatedAt       time.Time   `bson:"created_at" json:"created_at"`
	UpdatedAt       time.Time   `bson:"updated_at" json:"updated_at"`
	DeletedAt       *time.Time  `bson:"deleted_at" json:"deleted_at"`
}

// Save detection to MongoDB
func (m *MongoConnection) SaveDetection(ctx context.Context, detection *VisionDetection) error {
	collection := m.Database.Collection("vision_detections")
	_, err := collection.InsertOne(ctx, detection)
	return err
}

// Get detection by ID
func (m *MongoConnection) GetDetection(ctx context.Context, id string) (*VisionDetection, error) {
	// Implementation
}

// List user detections (paginated)
func (m *MongoConnection) ListDetections(ctx context.Context, userID string, limit, offset int) ([]*VisionDetection, error) {
	// Implementation
}
```

**File: `services/ml_service_go/internal/db/mongo.go`**
```go
// Similar structure for ML predictions and training history
```

### 4. Integration Steps

**Step 1**: Add MongoDB connection pooling to services
- Add MongoDB connection string env var
- Initialize connection on startup
- Add health check for MongoDB

**Step 2**: Update Vision Service handlers
- Modify Detect handler to save results to MongoDB
- Add new endpoints:
  - `GET /history` - List user's detections
  - `GET /history/:id` - Get specific detection
  - `DELETE /history/:id` - Soft delete detection

**Step 3**: Update ML Service handlers
- Modify training handler to track in MongoDB
- Save predictions to MongoDB
- Add new endpoints:
  - `GET /predictions` - List predictions
  - `GET /predictions/:id` - Get prediction
  - `GET /training-history` - List training sessions

**Step 4**: Update docker-compose
- Add MongoDB container (port 27017)
- Add MongoDB init scripts
- Update services with MONGODB_URI env var

## 🗂️ Files to Create/Modify

### New Files
```
services/vision_service_go/internal/db/mongo.go
services/vision_service_go/internal/db/models.go
services/ml_service_go/internal/db/mongo.go
services/ml_service_go/internal/db/models.go
scripts/mongodb-init.js          # Initialize collections and indices
docker-mongo-init/init.sh        # Docker entrypoint
```

### Modified Files
```
services/vision_service_go/internal/handler/vision.go        # Add MongoDB save
services/vision_service_go/internal/router/router.go         # Add new routes
services/ml_service_go/internal/handler/ml.go               # Add MongoDB save
services/ml_service_go/internal/router/router.go            # Add new routes
docker-compose.go.yml                                       # Add MongoDB service
```

## 📡 New API Endpoints

### Vision Service

```
GET  /history                    - List user's detections
GET  /history/:id               - Get specific detection
DELETE /history/:id             - Soft delete detection
GET  /history/search?class=cow  - Search detections by class
```

### ML Service

```
GET  /predictions               - List user's predictions
GET  /predictions/:id          - Get specific prediction
GET  /training-history         - List training sessions
GET  /training-history/:id     - Get specific training session
```

## 🚀 Quick Start (After Implementation)

```bash
# Start MongoDB
docker-compose -f docker-compose.go.yml up -d mongo

# Check MongoDB is ready
docker-compose -f docker-compose.go.yml exec mongo mongosh

# Initialize collections and indices
docker-compose -f docker-compose.go.yml exec mongo mongosh < scripts/mongodb-init.js

# Rebuild and start services
docker-compose -f docker-compose.go.yml up -d --build
```

## 💾 Backup Strategy

**Daily Backups**:
```bash
# Backup script
mongodump --uri="mongodb://localhost:27017/agrovision" --out=/backups/$(date +%Y%m%d)

# In docker
docker-compose exec mongo mongodump --out=/backups/daily_$(date +%Y%m%d)
```

## 📊 Query Examples

```javascript
// Total detections by user
db.vision_detections.aggregate([
  { $group: { _id: "$user_id", count: { $sum: 1 } } }
])

// Average confidence by class
db.vision_detections.aggregate([
  { $unwind: "$detections" },
  { $group: { 
      _id: "$detections.class", 
      avg_confidence: { $avg: "$detections.confidence" },
      count: { $sum: 1 }
    } 
  }
])

// Model performance
db.ml_training_history.aggregate([
  { $match: { status: "completed" } },
  { $sort: { "metrics.accuracy": -1 } },
  { $limit: 5 }
])

// Detection timeline
db.vision_detections.aggregate([
  { $match: { user_id: "user123" } },
  { $group: { 
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
      count: { $sum: 1 },
      avg_confidence: { $avg: { $avg: "$detections.confidence" } }
    } 
  },
  { $sort: { _id: -1 } }
])
```

## 🔐 Data Privacy & Security

- All data associated with user_id
- Soft deletes (deleted_at field)
- Encryption at rest (MongoDB Enterprise)
- IP whitelist in production
- Monthly data retention policy

## 📅 Timeline

- **Phase 1**: MongoDB setup & Go drivers (1-2 hours)
- **Phase 2**: Collection schema & indices (30 min)
- **Phase 3**: Vision Service integration (1 hour)
- **Phase 4**: ML Service integration (1 hour)
- **Phase 5**: Testing & documentation (1 hour)

**Total Estimated**: 4-5.5 hours

## ✅ Success Criteria

- [ ] MongoDB container running in docker-compose
- [ ] Collections created with correct indices
- [ ] Vision detections saved automatically
- [ ] ML predictions saved automatically
- [ ] Training history tracked
- [ ] All new endpoints tested
- [ ] Data retrieval working (history endpoints)
- [ ] Performance acceptable (< 500ms for queries)
