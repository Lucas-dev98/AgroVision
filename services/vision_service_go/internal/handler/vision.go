package handler

import (
	"bytes"
	"context"
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"strconv"
	"time"

	"agrovision/vision-service/internal/db"
	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

type DetectionResult struct {
	ID         string      `json:"id"`
	ImageURL   string      `json:"image_url"`
	Detections []Detection `json:"detections"`
	CreatedAt  string      `json:"created_at"`
}

type Detection struct {
	Class      string     `json:"class"`
	Confidence float64    `json:"confidence"`
	BBox       [4]float64 `json:"bbox"`
}

type VisionHandler struct {
	results           map[string]*DetectionResult
	yoloServiceURL    string
	detectionRepo     *db.VisionDetectionRepository
	mongoConnection   *db.MongoConnection
}

func NewVisionHandler(mongoConn *db.MongoConnection) *VisionHandler {
	yoloURL := os.Getenv("YOLO_SERVICE_URL")
	if yoloURL == "" {
		yoloURL = "http://localhost:8005"
	}

	var detectionRepo *db.VisionDetectionRepository
	if mongoConn != nil {
		detectionRepo = db.NewVisionDetectionRepository(mongoConn)
		// Create indices on startup
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		if err := detectionRepo.CreateIndices(ctx); err != nil {
			fmt.Printf("⚠ Warning: Failed to create indices: %v\n", err)
		}
		cancel()
	}

	return &VisionHandler{
		results:         make(map[string]*DetectionResult),
		yoloServiceURL:  yoloURL,
		detectionRepo:   detectionRepo,
		mongoConnection: mongoConn,
	}
}

// Detect handles image upload and YOLO detection
func (h *VisionHandler) Detect(c *gin.Context) {
	// Parse multipart form
	file, header, err := c.Request.FormFile("image")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Failed to parse image file",
		})
		return
	}
	defer file.Close()

	// Read image data
	imageData, err := io.ReadAll(file)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to read image file",
		})
		return
	}

	if len(imageData) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Empty image file",
		})
		return
	}

	// Extract metadata
	userID := c.GetString("user_id") // From JWT middleware (when available)
	animalID := c.Query("animal_id")
	imageHash := calculateHash(imageData)
	imageSizeKB := float64(len(imageData)) / 1024.0

	// Call Python YOLO service
	startTime := time.Now()
	detectionResult, yoloModelUsed, err := h.callYOLOService(imageData, header.Filename)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("YOLO detection failed: %v", err),
		})
		return
	}
	processingTimeMS := int(time.Since(startTime).Milliseconds())

	// Store result in memory (legacy)
	h.results[detectionResult.ID] = detectionResult

	// Convert detections for MongoDB
	detections := make([]db.Detection, len(detectionResult.Detections))
	for i, d := range detectionResult.Detections {
		detections[i] = db.Detection{
			Class:      d.Class,
			Confidence: d.Confidence,
			BBox:       d.BBox,
		}
	}

	// Save to MongoDB if available
	if h.detectionRepo != nil && h.mongoConnection != nil {
		parsedTime, _ := time.Parse(time.RFC3339, detectionResult.CreatedAt)
		detection := &db.VisionDetection{
			DetectionID:      detectionResult.ID,
			ImageURL:         detectionResult.ImageURL,
			ImageHash:        imageHash,
			ImageSizeKB:      imageSizeKB,
			Detections:       detections,
			ModelUsed:        yoloModelUsed,
			ProcessingTimeMS: processingTimeMS,
			UserID:           userID,
			AnimalID:         animalID,
			CreatedAt:        parsedTime,
		}

		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		_, err := h.detectionRepo.Save(ctx, detection)
		cancel()

		if err != nil {
			fmt.Printf("⚠ Warning: Failed to save detection to MongoDB: %v\n", err)
		}
	}

	c.JSON(http.StatusOK, detectionResult)
}

// callYOLOService sends image to Python YOLO service and returns detections
func (h *VisionHandler) callYOLOService(imageData []byte, filename string) (*DetectionResult, string, error) {
	// Create multipart request
	body := new(bytes.Buffer)
	writer := multipart.NewWriter(body)

	// Add file field
	part, err := writer.CreateFormFile("file", filename)
	if err != nil {
		return nil, "", fmt.Errorf("failed to create form file: %v", err)
	}

	_, err = io.Copy(part, bytes.NewReader(imageData))
	if err != nil {
		return nil, "", fmt.Errorf("failed to write file data: %v", err)
	}

	err = writer.Close()
	if err != nil {
		return nil, "", fmt.Errorf("failed to close writer: %v", err)
	}

	// Make HTTP request to YOLO service
	url := fmt.Sprintf("%s/detect", h.yoloServiceURL)
	req, err := http.NewRequest("POST", url, body)
	if err != nil {
		return nil, "", fmt.Errorf("failed to create request: %v", err)
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, "", fmt.Errorf("failed to call YOLO service: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, "", fmt.Errorf("YOLO service returned status %d: %s", resp.StatusCode, string(body))
	}

	// Parse response
	var yoloResp struct {
		ID         string      `json:"id"`
		ImageURL   string      `json:"image_url"`
		Detections []Detection `json:"detections"`
		ModelUsed  string      `json:"model_used"`
		CreatedAt  string      `json:"created_at"`
	}

	err = json.NewDecoder(resp.Body).Decode(&yoloResp)
	if err != nil {
		return nil, "", fmt.Errorf("failed to parse YOLO response: %v", err)
	}

	// Create result
	result := &DetectionResult{
		ID:         yoloResp.ID,
		ImageURL:   yoloResp.ImageURL,
		Detections: yoloResp.Detections,
		CreatedAt:  yoloResp.CreatedAt,
	}

	return result, yoloResp.ModelUsed, nil
}

// GetResult retrieves a detection result by ID
func (h *VisionHandler) GetResult(c *gin.Context) {
	resultID := c.Param("id")

	result, exists := h.results[resultID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Detection result not found",
		})
		return
	}

	c.JSON(http.StatusOK, result)
}

// ListResults lists all detection results
func (h *VisionHandler) ListResults(c *gin.Context) {
	results := make([]*DetectionResult, 0)
	for _, result := range h.results {
		results = append(results, result)
	}

	c.JSON(http.StatusOK, gin.H{
		"results": results,
		"total":   len(results),
	})
}

// GetHistory retrieves detection history from MongoDB
func (h *VisionHandler) GetHistory(c *gin.Context) {
	if h.detectionRepo == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"error": "MongoDB not available",
		})
		return
	}

	detectionID := c.Param("id")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	detection, err := h.detectionRepo.GetByID(ctx, detectionID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "Detection not found",
		})
		return
	}

	c.JSON(http.StatusOK, detection)
}

// ListHistory retrieves user's detection history from MongoDB
func (h *VisionHandler) ListHistory(c *gin.Context) {
	if h.detectionRepo == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"error": "MongoDB not available",
		})
		return
	}

	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "User ID not found in context",
		})
		return
	}

	// Pagination
	limit := int64(20)
	if l := c.Query("limit"); l != "" {
		if parsed, err := strconv.ParseInt(l, 10, 64); err == nil && parsed > 0 && parsed <= 100 {
			limit = parsed
		}
	}

	skip := int64(0)
	if s := c.Query("skip"); s != "" {
		if parsed, err := strconv.ParseInt(s, 10, 64); err == nil && parsed >= 0 {
			skip = parsed
		}
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	detections, err := h.detectionRepo.ListByUser(ctx, userID, limit, skip)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("Failed to retrieve history: %v", err),
		})
		return
	}

	count, _ := h.detectionRepo.CountByUser(context.Background(), userID)

	c.JSON(http.StatusOK, gin.H{
		"detections": detections,
		"total":      count,
		"limit":      limit,
		"skip":       skip,
	})
}

// SearchByClass searches detections by animal class
func (h *VisionHandler) SearchByClass(c *gin.Context) {
	if h.detectionRepo == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"error": "MongoDB not available",
		})
		return
	}

	class := c.Query("class")
	if class == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Class parameter is required",
		})
		return
	}

	limit := int64(20)
	if l := c.Query("limit"); l != "" {
		if parsed, err := strconv.ParseInt(l, 10, 64); err == nil && parsed > 0 {
			limit = parsed
		}
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	detections, err := h.detectionRepo.SearchByClass(ctx, class, limit, 0)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("Search failed: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"detections": detections,
		"class":      class,
		"count":      len(detections),
	})
}

// DeleteHistory soft deletes a detection
func (h *VisionHandler) DeleteHistory(c *gin.Context) {
	if h.detectionRepo == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"error": "MongoDB not available",
		})
		return
	}

	detectionID := c.Param("id")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	err := h.detectionRepo.Delete(ctx, detectionID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("Failed to delete detection: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Detection deleted successfully",
		"id":      detectionID,
	})
}

// GetStatistics returns detection statistics
func (h *VisionHandler) GetStatistics(c *gin.Context) {
	if h.detectionRepo == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"error": "MongoDB not available",
		})
		return
	}

	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{
			"error": "User ID not found in context",
		})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	stats, err := h.detectionRepo.GetStatistics(ctx, userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("Failed to get statistics: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, stats)
}

// Health check
func (h *VisionHandler) Health(c *gin.Context) {
	status := "ok"
	mongoStatus := "disconnected"

	if h.mongoConnection != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		if err := h.mongoConnection.Health(ctx); err == nil {
			mongoStatus = "connected"
		}
		cancel()
	}

	c.JSON(http.StatusOK, gin.H{
		"status":        status,
		"service":       "vision-service",
		"yolo_service":  h.yoloServiceURL,
		"mongodb":       mongoStatus,
	})
}

// Helper function to calculate MD5 hash of image data
func calculateHash(data []byte) string {
	hash := md5.Sum(data)
	return hex.EncodeToString(hash[:])
}
