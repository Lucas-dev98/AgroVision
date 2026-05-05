package db
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

// MLPrediction represents a model prediction stored in MongoDB
type MLPrediction struct {
	ID             primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	PredictionID   string             `bson:"prediction_id" json:"prediction_id"`
	ModelID        string             `bson:"model_id" json:"model_id"`
	ModelName      string             `bson:"model_name" json:"model_name"`
	Input          map[string]interface{} `bson:"input" json:"input"`
	Output         map[string]interface{} `bson:"output" json:"output"`
	Confidence     float64            `bson:"confidence" json:"confidence"`
	ProcessingTimeMS int               `bson:"processing_time_ms" json:"processing_time_ms"`
	UserID         string             `bson:"user_id" json:"user_id"`
	AnimalID       string             `bson:"animal_id" json:"animal_id"`
	CreatedAt      time.Time          `bson:"created_at" json:"created_at"`
	UpdatedAt      time.Time          `bson:"updated_at" json:"updated_at"`
	DeletedAt      *time.Time         `bson:"deleted_at" json:"deleted_at"`
}

// MLTrainingHistory represents a training session stored in MongoDB
type MLTrainingHistory struct {
	ID                   primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	TrainingID           string             `bson:"training_id" json:"training_id"`
	ModelID              string             `bson:"model_id" json:"model_id"`
	ModelName            string             `bson:"model_name" json:"model_name"`
	Status               string             `bson:"status" json:"status"` // pending, training, completed, failed
	Parameters           map[string]interface{} `bson:"parameters" json:"parameters"`
	Metrics              map[string]interface{} `bson:"metrics" json:"metrics"`
	DurationSeconds      int64              `bson:"duration_seconds" json:"duration_seconds"`
	DatasetID            string             `bson:"dataset_id" json:"dataset_id"`
	DataAugmentation     bool               `bson:"data_augmentation" json:"data_augmentation"`
	UserID               string             `bson:"user_id" json:"user_id"`
	Notes                string             `bson:"notes" json:"notes"`
	StartedAt            time.Time          `bson:"started_at" json:"started_at"`
	CompletedAt          *time.Time         `bson:"completed_at" json:"completed_at"`
	ErrorMessage         *string            `bson:"error_message" json:"error_message"`
	CreatedAt            time.Time          `bson:"created_at" json:"created_at"`
	UpdatedAt            time.Time          `bson:"updated_at" json:"updated_at"`
}

// MLPredictionRepository handles database operations for ML predictions
type MLPredictionRepository struct {
	collection *mongo.Collection
}

// NewMLPredictionRepository creates a new repository
func NewMLPredictionRepository(mc *MongoConnection) *MLPredictionRepository {
	return &MLPredictionRepository{
		collection: mc.Database.Collection("ml_predictions"),
	}
}

// Save stores a prediction in MongoDB
func (r *MLPredictionRepository) Save(ctx context.Context, prediction *MLPrediction) (string, error) {
	if prediction.CreatedAt.IsZero() {
		prediction.CreatedAt = time.Now().UTC()
	}
	prediction.UpdatedAt = time.Now().UTC()

	result, err := r.collection.InsertOne(ctx, prediction)
	if err != nil {
		return "", fmt.Errorf("failed to save prediction: %w", err)
	}

	return result.InsertedID.(primitive.ObjectID).Hex(), nil
}

// GetByID retrieves a prediction by ID
func (r *MLPredictionRepository) GetByID(ctx context.Context, id string) (*MLPrediction, error) {
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return nil, fmt.Errorf("invalid prediction ID: %w", err)
	}

	var prediction MLPrediction
	err = r.collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&prediction)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return nil, fmt.Errorf("prediction not found")
		}
		return nil, fmt.Errorf("failed to get prediction: %w", err)
	}

	return &prediction, nil
}

// ListByUser retrieves predictions for a user (paginated)
func (r *MLPredictionRepository) ListByUser(ctx context.Context, userID string, limit, skip int64) ([]*MLPrediction, error) {
	opts := options.Find().
		SetSort(bson.M{"created_at": -1}).
		SetLimit(limit).
		SetSkip(skip)

	cursor, err := r.collection.Find(ctx, bson.M{
		"user_id":   userID,
		"deleted_at": nil,
	}, opts)
	if err != nil {
		return nil, fmt.Errorf("failed to query predictions: %w", err)
	}
	defer cursor.Close(ctx)

	var predictions []*MLPrediction
	if err = cursor.All(ctx, &predictions); err != nil {
		return nil, fmt.Errorf("failed to decode predictions: %w", err)
	}

	return predictions, nil
}

// ListByModel retrieves predictions for a specific model
func (r *MLPredictionRepository) ListByModel(ctx context.Context, modelID string, limit, skip int64) ([]*MLPrediction, error) {
	opts := options.Find().
		SetSort(bson.M{"created_at": -1}).
		SetLimit(limit).
		SetSkip(skip)

	cursor, err := r.collection.Find(ctx, bson.M{
		"model_id":  modelID,
		"deleted_at": nil,
	}, opts)
	if err != nil {
		return nil, fmt.Errorf("failed to query predictions: %w", err)
	}
	defer cursor.Close(ctx)

	var predictions []*MLPrediction
	if err = cursor.All(ctx, &predictions); err != nil {
		return nil, fmt.Errorf("failed to decode predictions: %w", err)
	}

	return predictions, nil
}

// CountByUser counts predictions for a user
func (r *MLPredictionRepository) CountByUser(ctx context.Context, userID string) (int64, error) {
	count, err := r.collection.CountDocuments(ctx, bson.M{
		"user_id":   userID,
		"deleted_at": nil,
	})
	if err != nil {
		return 0, fmt.Errorf("failed to count predictions: %w", err)
	}
	return count, nil
}

// CreateIndices creates necessary indices for performance
func (r *MLPredictionRepository) CreateIndices(ctx context.Context) error {
	indexModel := []mongo.IndexModel{
		{
			Keys: bson.D{{Key: "user_id", Value: 1}, {Key: "created_at", Value: -1}},
		},
		{
			Keys: bson.D{{Key: "model_id", Value: 1}, {Key: "created_at", Value: -1}},
		},
		{
			Keys: bson.D{{Key: "animal_id", Value: 1}},
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

// MLTrainingRepository handles database operations for training history
type MLTrainingRepository struct {
	collection *mongo.Collection
}

// NewMLTrainingRepository creates a new repository
func NewMLTrainingRepository(mc *MongoConnection) *MLTrainingRepository {
	return &MLTrainingRepository{
		collection: mc.Database.Collection("ml_training_history"),
	}
}

// Save stores training history in MongoDB
func (r *MLTrainingRepository) Save(ctx context.Context, training *MLTrainingHistory) (string, error) {
	if training.CreatedAt.IsZero() {
		training.CreatedAt = time.Now().UTC()
	}
	training.UpdatedAt = time.Now().UTC()

	result, err := r.collection.InsertOne(ctx, training)
	if err != nil {
		return "", fmt.Errorf("failed to save training: %w", err)
	}

	return result.InsertedID.(primitive.ObjectID).Hex(), nil
}

// GetByID retrieves training by ID
func (r *MLTrainingRepository) GetByID(ctx context.Context, id string) (*MLTrainingHistory, error) {
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return nil, fmt.Errorf("invalid training ID: %w", err)
	}

	var training MLTrainingHistory
	err = r.collection.FindOne(ctx, bson.M{"_id": objID}).Decode(&training)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return nil, fmt.Errorf("training not found")
		}
		return nil, fmt.Errorf("failed to get training: %w", err)
	}

	return &training, nil
}

// ListByModel retrieves training history for a model
func (r *MLTrainingRepository) ListByModel(ctx context.Context, modelID string, limit, skip int64) ([]*MLTrainingHistory, error) {
	opts := options.Find().
		SetSort(bson.M{"created_at": -1}).
		SetLimit(limit).
		SetSkip(skip)

	cursor, err := r.collection.Find(ctx, bson.M{"model_id": modelID}, opts)
	if err != nil {
		return nil, fmt.Errorf("failed to query training: %w", err)
	}
	defer cursor.Close(ctx)

	var training []*MLTrainingHistory
	if err = cursor.All(ctx, &training); err != nil {
		return nil, fmt.Errorf("failed to decode training: %w", err)
	}

	return training, nil
}

// ListByUser retrieves training for a user
func (r *MLTrainingRepository) ListByUser(ctx context.Context, userID string, limit, skip int64) ([]*MLTrainingHistory, error) {
	opts := options.Find().
		SetSort(bson.M{"created_at": -1}).
		SetLimit(limit).
		SetSkip(skip)

	cursor, err := r.collection.Find(ctx, bson.M{"user_id": userID}, opts)
	if err != nil {
		return nil, fmt.Errorf("failed to query training: %w", err)
	}
	defer cursor.Close(ctx)

	var training []*MLTrainingHistory
	if err = cursor.All(ctx, &training); err != nil {
		return nil, fmt.Errorf("failed to decode training: %w", err)
	}

	return training, nil
}

// UpdateStatus updates training status
func (r *MLTrainingRepository) UpdateStatus(ctx context.Context, id string, status string) error {
	objID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return fmt.Errorf("invalid training ID: %w", err)
	}

	now := time.Now().UTC()
	update := bson.M{
		"$set": bson.M{
			"status":     status,
			"updated_at": now,
		},
	}

	if status == "completed" {
		update["$set"].(bson.M)["completed_at"] = &now
	}

	_, err = r.collection.UpdateOne(ctx, bson.M{"_id": objID}, update)
	if err != nil {
		return fmt.Errorf("failed to update training: %w", err)
	}

	return nil
}

// CreateIndices creates necessary indices
func (r *MLTrainingRepository) CreateIndices(ctx context.Context) error {
	indexModel := []mongo.IndexModel{
		{
			Keys: bson.D{{Key: "model_id", Value: 1}, {Key: "created_at", Value: -1}},
		},
		{
			Keys: bson.D{{Key: "user_id", Value: 1}, {Key: "created_at", Value: -1}},
		},
		{
			Keys: bson.D{{Key: "status", Value: 1}},
		},
		{
			Keys: bson.D{{Key: "started_at", Value: 1}},
		},
	}

	opts := options.CreateIndexes().SetMaxTime(10 * time.Second)
	_, err := r.collection.Indexes().CreateMany(ctx, indexModel, opts)
	if err != nil {
		return fmt.Errorf("failed to create indices: %w", err)
	}

	return nil
}
