package db

import (
	"context"
	"fmt"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// VisionDetection represents a YOLO detection result stored in MongoDB
type VisionDetection struct {
	ID               primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	DetectionID      string             `bson:"detection_id" json:"detection_id"`
	ImageURL         string             `bson:"image_url" json:"image_url"`
	ImageHash        string             `bson:"image_hash" json:"image_hash"`
	ImageSizeKB      float64            `bson:"image_size_kb" json:"image_size_kb"`
	Detections       []Detection        `bson:"detections" json:"detections"`
	ModelUsed        string             `bson:"model_used" json:"model_used"`
	ProcessingTimeMS int                `bson:"processing_time_ms" json:"processing_time_ms"`
	UserID           string             `bson:"user_id" json:"user_id"`
	AnimalID         string             `bson:"animal_id" json:"animal_id"`
	CreatedAt        time.Time          `bson:"created_at" json:"created_at"`
	UpdatedAt        time.Time          `bson:"updated_at" json:"updated_at"`
	DeletedAt        *time.Time         `bson:"deleted_at" json:"deleted_at"`
}

// Detection represents a single YOLO detection
type Detection struct {
	Class      string     `bson:"class" json:"class"`
	Confidence float64    `bson:"confidence" json:"confidence"`
	BBox       [4]float64 `bson:"bbox" json:"bbox"`
}

// VisionDetectionRepository handles database operations for vision detections
type VisionDetectionRepository struct {
	collection *mongo.Collection
}

// NewVisionDetectionRepository creates a new repository
func NewVisionDetectionRepository(mc *MongoConnection) *VisionDetectionRepository {
	return &VisionDetectionRepository{
		collection: mc.Database.Collection("vision_detections"),
	}
}

// Save stores a detection result in MongoDB
func (r *VisionDetectionRepository) Save(ctx context.Context, detection *VisionDetection) (string, error) {
	if detection.CreatedAt.IsZero() {
		detection.CreatedAt = time.Now().UTC()
	}
	detection.UpdatedAt = time.Now().UTC()

	result, err := r.collection.InsertOne(ctx, detection)
	if err != nil {
		return "", fmt.Errorf("failed to save detection: %w", err)
	}

	return result.InsertedID.(primitive.ObjectID).Hex(), nil
}

// GetByID retrieves a detection by its ID
func (r *VisionDetectionRepository) GetByID(ctx context.Context, id string) (*VisionDetection, error) {
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return nil, fmt.Errorf("invalid detection ID: %w", err)
	}

	var detection VisionDetection
	err = r.collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&detection)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return nil, fmt.Errorf("detection not found")
		}
		return nil, fmt.Errorf("failed to get detection: %w", err)
	}

	return &detection, nil
}

// ListByUser retrieves all detections for a user (paginated, most recent first)
func (r *VisionDetectionRepository) ListByUser(ctx context.Context, userID string, limit, skip int64) ([]*VisionDetection, error) {
	opts := options.Find().
		SetSort(bson.M{"created_at": -1}).
		SetLimit(limit).
		SetSkip(skip)

	cursor, err := r.collection.Find(ctx, bson.M{
		"user_id":   userID,
		"deleted_at": nil,
	}, opts)
	if err != nil {
		return nil, fmt.Errorf("failed to query detections: %w", err)
	}
	defer cursor.Close(ctx)

	var detections []*VisionDetection
	if err = cursor.All(ctx, &detections); err != nil {
		return nil, fmt.Errorf("failed to decode detections: %w", err)
	}

	return detections, nil
}

// ListByAnimal retrieves all detections for a specific animal
func (r *VisionDetectionRepository) ListByAnimal(ctx context.Context, animalID string, limit, skip int64) ([]*VisionDetection, error) {
	opts := options.Find().
		SetSort(bson.M{"created_at": -1}).
		SetLimit(limit).
		SetSkip(skip)

	cursor, err := r.collection.Find(ctx, bson.M{
		"animal_id":  animalID,
		"deleted_at": nil,
	}, opts)
	if err != nil {
		return nil, fmt.Errorf("failed to query detections: %w", err)
	}
	defer cursor.Close(ctx)

	var detections []*VisionDetection
	if err = cursor.All(ctx, &detections); err != nil {
		return nil, fmt.Errorf("failed to decode detections: %w", err)
	}

	return detections, nil
}

// SearchByClass finds detections by animal class (e.g., "cow", "horse")
func (r *VisionDetectionRepository) SearchByClass(ctx context.Context, class string, limit, skip int64) ([]*VisionDetection, error) {
	opts := options.Find().
		SetSort(bson.M{"created_at": -1}).
		SetLimit(limit).
		SetSkip(skip)

	cursor, err := r.collection.Find(ctx, bson.M{
		"detections.class": class,
		"deleted_at":       nil,
	}, opts)
	if err != nil {
		return nil, fmt.Errorf("failed to query detections: %w", err)
	}
	defer cursor.Close(ctx)

	var detections []*VisionDetection
	if err = cursor.All(ctx, &detections); err != nil {
		return nil, fmt.Errorf("failed to decode detections: %w", err)
	}

	return detections, nil
}

// CountByUser counts detections for a user
func (r *VisionDetectionRepository) CountByUser(ctx context.Context, userID string) (int64, error) {
	count, err := r.collection.CountDocuments(ctx, bson.M{
		"user_id":   userID,
		"deleted_at": nil,
	})
	if err != nil {
		return 0, fmt.Errorf("failed to count detections: %w", err)
	}
	return count, nil
}

// Delete soft deletes a detection
func (r *VisionDetectionRepository) Delete(ctx context.Context, id string) error {
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return fmt.Errorf("invalid detection ID: %w", err)
	}

	now := time.Now().UTC()
	_, err = r.collection.UpdateOne(ctx, bson.M{"_id": objID}, bson.M{
		"$set": bson.M{
			"deleted_at": now,
			"updated_at": now,
		},
	})

	if err != nil {
		return fmt.Errorf("failed to delete detection: %w", err)
	}

	return nil
}

// GetStatistics returns detection statistics for a user
func (r *VisionDetectionRepository) GetStatistics(ctx context.Context, userID string) (map[string]interface{}, error) {
	pipeline := mongo.Pipeline{
		bson.D{
			{Key: "$match", Value: bson.M{
				"user_id":   userID,
				"deleted_at": nil,
			}},
		},
		bson.D{
			{Key: "$group", Value: bson.M{
				"_id":           nil,
				"total_detections": bson.M{"$sum": 1},
				"avg_confidence": bson.M{"$avg": bson.M{
					"$avg": "$detections.confidence",
				}},
				"models_used": bson.M{"$addToSet": "$model_used"},
				"total_animals": bson.M{"$sum": bson.M{"$size": "$detections"}},
			}},
		},
	}

	cursor, err := r.collection.Aggregate(ctx, pipeline)
	if err != nil {
		return nil, fmt.Errorf("failed to aggregate statistics: %w", err)
	}
	defer cursor.Close(ctx)

	var results []map[string]interface{}
	if err = cursor.All(ctx, &results); err != nil {
		return nil, fmt.Errorf("failed to decode statistics: %w", err)
	}

	if len(results) == 0 {
		return map[string]interface{}{
			"total_detections": 0,
			"avg_confidence":   0,
			"models_used":      []string{},
			"total_animals":    0,
		}, nil
	}

	return results[0], nil
}

// CreateIndices creates necessary indices for performance
func (r *VisionDetectionRepository) CreateIndices(ctx context.Context) error {
	indexModel := []mongo.IndexModel{
		{
			Keys: bson.D{{Key: "user_id", Value: 1}, {Key: "created_at", Value: -1}},
		},
		{
			Keys: bson.D{{Key: "animal_id", Value: 1}, {Key: "created_at", Value: -1}},
		},
		{
			Keys: bson.D{{Key: "image_hash", Value: 1}},
		},
		{
			Keys: bson.D{{Key: "model_used", Value: 1}},
		},
		{
			Keys: bson.D{{Key: "detections.class", Value: 1}},
		},
		{
			Keys: bson.D{{Key: "created_at", Value: -1}},
		},
	}

	opts := options.CreateIndexes().SetMaxTime(10 * time.Second)
	_, err := r.collection.Indexes().CreateMany(ctx, indexModel, opts)
	if err != nil {
		return fmt.Errorf("failed to create indices: %w", err)
	}

	return nil
}
