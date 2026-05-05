package handler
package handler

import (
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type DetectionResult struct {
	ID        string    `json:"id"`
	ImageURL  string    `json:"image_url"`
	Detections []Detection `json:"detections"`
	CreatedAt string    `json:"created_at"`
}

type Detection struct {
	Class      string    `json:"class"`
	Confidence float64   `json:"confidence"`
	BBox       [4]float64 `json:"bbox"`
}

type VisionHandler struct {
	results map[string]*DetectionResult
}

func NewVisionHandler() *VisionHandler {
	return &VisionHandler{
		results: make(map[string]*DetectionResult),
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

	// Simulate image processing - in production, this would run YOLO
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

	// Simulate YOLO detection (mock)
	detections := h.simulateYOLODetection(header.Filename)

	// Create result
	resultID := uuid.New().String()
	result := &DetectionResult{
		ID:         resultID,
		ImageURL:   fmt.Sprintf("file://%s", header.Filename),
		Detections: detections,
		CreatedAt:  time.Now().UTC().Format(time.RFC3339),
	}

	// Store result
	h.results[resultID] = result

	c.JSON(http.StatusOK, result)
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

// simulateYOLODetection simulates YOLO detection (mock)
// In production, this would call actual YOLO model
func (h *VisionHandler) simulateYOLODetection(filename string) []Detection {
	rand.Seed(time.Now().UnixNano())

	// Random number of detections (1-3)
	numDetections := rand.Intn(3) + 1
	detections := make([]Detection, numDetections)

	for i := 0; i < numDetections; i++ {
		detections[i] = Detection{
			Class:      "animal",
			Confidence: 0.85 + rand.Float64()*0.15, // 0.85 - 1.0
			BBox: [4]float64{
				float64(rand.Intn(200)),           // x1
				float64(rand.Intn(200)),           // y1
				float64(200 + rand.Intn(400)),     // x2
				float64(200 + rand.Intn(400)),     // y2
			},
		}
	}

	return detections
}

// Health check
func (h *VisionHandler) Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "ok",
		"service": "vision-service",
	})
}
