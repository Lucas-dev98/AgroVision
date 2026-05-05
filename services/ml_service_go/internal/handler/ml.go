package handler

import (
	"context"
	"fmt"
	"math/rand"
	"net/http"
	"strconv"
	"time"

	"github.com/agrovision/ml-service/internal/db"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

type MLModel struct {
	ID           string  `json:"id"`
	Name         string  `json:"name"`
	Type         string  `json:"type"`
	Status       string  `json:"status"`
	Accuracy     *float64 `json:"accuracy,omitempty"`
	LastTrained  *string  `json:"last_trained,omitempty"`
	Version      string  `json:"version"`
}

type PredictionResult struct {
	ID         string  `json:"id"`
	ModelID    string  `json:"model_id"`
	Input      string  `json:"input"`
	Output     string  `json:"output"`
	Confidence float64 `json:"confidence"`
	CreatedAt  string  `json:"created_at"`
}

type TrainingRequest struct {
	ModelID      string `json:"model_id"`
	Epochs       int    `json:"epochs"`
	BatchSize    int    `json:"batch_size"`
	LearningRate float64 `json:"learning_rate"`
}

type PredictionRequest struct {
	ModelID string `json:"model_id"`
	Input   string `json:"input"`
}

type MLHandler struct {
	models              map[string]*MLModel
	predictions         map[string]*PredictionResult
	mongoConnection     *db.MongoConnection
	predictionRepo      *db.MLPredictionRepository
	trainingHistoryRepo *db.MLTrainingRepository
}

func NewMLHandler(mongoConnection *db.MongoConnection) *MLHandler {
	handler := &MLHandler{
		models:          make(map[string]*MLModel),
		predictions:     make(map[string]*PredictionResult),
		mongoConnection: mongoConnection,
	}

	// Initialize repositories if MongoDB is available
	if mongoConnection != nil {
		handler.predictionRepo = &db.MLPredictionRepository{
			Collection: mongoConnection.DB.Collection("ml_predictions"),
		}
		handler.trainingHistoryRepo = &db.MLTrainingRepository{
			Collection: mongoConnection.DB.Collection("ml_training_history"),
		}

		// Create indices
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		handler.predictionRepo.CreateIndices(ctx)
		handler.trainingHistoryRepo.CreateIndices(ctx)
	}

	// Initialize with mock models
	handler.initializeMockModels()

	return handler
}

func (h *MLHandler) initializeMockModels() {
	now := time.Now().UTC()
	sevenDaysAgo := now.AddDate(0, 0, -7).Format(time.RFC3339)
	fourteenDaysAgo := now.AddDate(0, 0, -14).Format(time.RFC3339)

	accuracy94 := 0.94
	accuracy88 := 0.88

	h.models["model_1"] = &MLModel{
		ID:          "model_1",
		Name:        "Detecção de Anomalias",
		Type:        "anomaly_detection",
		Status:      "active",
		Accuracy:    &accuracy94,
		LastTrained: &sevenDaysAgo,
		Version:     "2.1.0",
	}

	h.models["model_2"] = &MLModel{
		ID:          "model_2",
		Name:        "Classificação de Comportamento",
		Type:        "behavior_classification",
		Status:      "active",
		Accuracy:    &accuracy88,
		LastTrained: &fourteenDaysAgo,
		Version:     "1.5.0",
	}

	h.models["model_3"] = &MLModel{
		ID:      "model_3",
		Name:    "Predição de Peso",
		Type:    "prediction",
		Status:  "training",
		Version: "3.0.0-beta",
	}
}

// GetModels returns all available models
func (h *MLHandler) GetModels(c *gin.Context) {
	models := make([]*MLModel, 0)
	for _, model := range h.models {
		models = append(models, model)
	}

	c.JSON(http.StatusOK, gin.H{
		"models": models,
		"total":  len(models),
	})
}

// GetModel returns a specific model
func (h *MLHandler) GetModel(c *gin.Context) {
	modelID := c.Param("id")

	model, exists := h.models[modelID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Model not found",
		})
		return
	}

	c.JSON(http.StatusOK, model)
}

// Train starts training a model
func (h *MLHandler) Train(c *gin.Context) {
	var req TrainingRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid request",
		})
		return
	}

	model, exists := h.models[req.ModelID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Model not found",
		})
		return
	}

	// Extract user_id from context (from JWT)
	userID := c.GetString("user_id")

	// Update model status to training
	oldStatus := model.Status
	model.Status = "training"

	// Create training history record
	trainingID := uuid.New().String()
	trainingRecord := &db.MLTrainingHistory{
		TrainingID: trainingID,
		ModelID:    req.ModelID,
		Status:     "training",
		Parameters: map[string]interface{}{
			"epochs":        req.Epochs,
			"batch_size":    req.BatchSize,
			"learning_rate": req.LearningRate,
		},
		UserID:    userID,
		StartedAt: time.Now(),
	}

	// Save to MongoDB if available
	if h.trainingHistoryRepo != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		h.trainingHistoryRepo.Save(ctx, trainingRecord)
		cancel()
	}

	// Simulate training in background
	go func() {
		time.Sleep(5 * time.Second)

		// Update status and accuracy after training
		now := time.Now().UTC().Format(time.RFC3339)
		accuracy := 0.85 + rand.Float64()*0.15

		model.Status = "active"
		model.Accuracy = &accuracy
		model.LastTrained = &now

		// Update training record in MongoDB
		if h.trainingHistoryRepo != nil {
			ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
			trainingRecord.Status = "completed"
			trainingRecord.CompletedAt = time.Now()
			trainingRecord.Metrics = map[string]interface{}{
				"accuracy": accuracy,
				"loss":     0.05 + rand.Float64()*0.1,
			}
			trainingRecord.DurationSeconds = int64(time.Since(trainingRecord.StartedAt).Seconds())
			h.trainingHistoryRepo.UpdateStatus(ctx, trainingRecord.TrainingID, trainingRecord)
			cancel()
		}
	}()

	c.JSON(http.StatusOK, gin.H{
		"message":      "Training started",
		"training_id":  trainingID,
		"model_id":     req.ModelID,
		"old_status":   oldStatus,
		"new_status":   model.Status,
		"epochs":       req.Epochs,
		"batch_size":   req.BatchSize,
		"learning_rate": req.LearningRate,
	})
}

// Predict makes a prediction using a model
func (h *MLHandler) Predict(c *gin.Context) {
	var req PredictionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid request",
		})
		return
	}

	model, exists := h.models[req.ModelID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Model not found",
		})
		return
	}

	if model.Status == "training" {
		c.JSON(http.StatusConflict, gin.H{
			"error": "Model is currently training",
		})
		return
	}

	// Extract user_id from context (from JWT)
	userID := c.GetString("user_id")
	animalID := c.Query("animal_id")

	// Measure prediction time
	startTime := time.Now()

	// Simulate prediction
	output := fmt.Sprintf("Resultado simulado para: %s (usando %s v%s)", req.Input, model.Name, model.Version)
	confidence := 0.60 + rand.Float64()*0.40

	processingTimeMS := int(time.Since(startTime).Milliseconds())

	// Create prediction result
	result := &PredictionResult{
		ID:         uuid.New().String(),
		ModelID:    req.ModelID,
		Input:      req.Input,
		Output:     output,
		Confidence: confidence,
		CreatedAt:  time.Now().UTC().Format(time.RFC3339),
	}

	// Store in in-memory cache
	h.predictions[result.ID] = result

	// Save to MongoDB if available
	if h.predictionRepo != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		prediction := &db.MLPrediction{
			PredictionID:    result.ID,
			ModelID:         req.ModelID,
			Input:           map[string]interface{}{"raw": req.Input},
			Output:          map[string]interface{}{"result": output},
			Confidence:      confidence,
			ProcessingTimeMS: processingTimeMS,
			UserID:          userID,
			AnimalID:        animalID,
			CreatedAt:       time.Now(),
		}
		h.predictionRepo.Save(ctx, prediction)
		cancel()
	}

	c.JSON(http.StatusOK, result)
}

// GetPredictions returns all predictions
func (h *MLHandler) GetPredictions(c *gin.Context) {
	results := make([]*PredictionResult, 0)
	for _, result := range h.predictions {
		results = append(results, result)
	}

	c.JSON(http.StatusOK, gin.H{
		"predictions": results,
		"total":       len(results),
	})
}

// GetPrediction returns a specific prediction
func (h *MLHandler) GetPrediction(c *gin.Context) {
	predictionID := c.Param("id")

	prediction, exists := h.predictions[predictionID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Prediction not found",
		})
		return
	}

	c.JSON(http.StatusOK, prediction)
}

// GetPredictionHistory returns user's prediction history from MongoDB
func (h *MLHandler) GetPredictionHistory(c *gin.Context) {
	if h.predictionRepo == nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "MongoDB not configured",
		})
		return
	}

	userID := c.GetString("user_id")
	limitStr := c.Query("limit")
	skipStr := c.Query("skip")

	limit := int64(20)
	skip := int64(0)

	if l, err := strconv.ParseInt(limitStr, 10, 64); err == nil {
		limit = l
	}
	if s, err := strconv.ParseInt(skipStr, 10, 64); err == nil {
		skip = s
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	predictions, err := h.predictionRepo.ListByUser(ctx, userID, limit, skip)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch predictions",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"predictions": predictions,
		"limit":       limit,
		"skip":        skip,
	})
}

// GetTrainingHistory returns user's training history from MongoDB
func (h *MLHandler) GetTrainingHistory(c *gin.Context) {
	if h.trainingHistoryRepo == nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "MongoDB not configured",
		})
		return
	}

	userID := c.GetString("user_id")
	limitStr := c.Query("limit")
	skipStr := c.Query("skip")

	limit := int64(20)
	skip := int64(0)

	if l, err := strconv.ParseInt(limitStr, 10, 64); err == nil {
		limit = l
	}
	if s, err := strconv.ParseInt(skipStr, 10, 64); err == nil {
		skip = s
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	trainings, err := h.trainingHistoryRepo.ListByUser(ctx, userID, limit, skip)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch training history",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"trainings": trainings,
		"limit":     limit,
		"skip":      skip,
	})
}

// GetTrainingHistoryByModel returns training history for specific model
func (h *MLHandler) GetTrainingHistoryByModel(c *gin.Context) {
	if h.trainingHistoryRepo == nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "MongoDB not configured",
		})
		return
	}

	modelID := c.Param("model_id")
	limitStr := c.Query("limit")
	skipStr := c.Query("skip")

	limit := int64(20)
	skip := int64(0)

	if l, err := strconv.ParseInt(limitStr, 10, 64); err == nil {
		limit = l
	}
	if s, err := strconv.ParseInt(skipStr, 10, 64); err == nil {
		skip = s
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	trainings, err := h.trainingHistoryRepo.ListByModel(ctx, modelID, limit, skip)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to fetch training history",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"trainings": trainings,
		"limit":     limit,
		"skip":      skip,
	})
}

// Health check
func (h *MLHandler) Health(c *gin.Context) {
	mongoStatus := "ok"
	if h.mongoConnection != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		if err := h.mongoConnection.Health(ctx); err != nil {
			mongoStatus = "error"
		}
		cancel()
	}

	c.JSON(http.StatusOK, gin.H{
		"status":  "ok",
		"service": "ml-service",
		"mongodb": mongoStatus,
	})
}
