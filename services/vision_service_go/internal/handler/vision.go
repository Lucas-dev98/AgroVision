package handler

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
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
	results          map[string]*DetectionResult
	yoloServiceURL   string
}

func NewVisionHandler() *VisionHandler {
	yoloURL := os.Getenv("YOLO_SERVICE_URL")
	if yoloURL == "" {
		yoloURL = "http://localhost:8005"
	}
	
	return &VisionHandler{
		results:        make(map[string]*DetectionResult),
		yoloServiceURL: yoloURL,
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

	// Call Python YOLO service
	detectionResult, err := h.callYOLOService(imageData, header.Filename)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("YOLO detection failed: %v", err),
		})
		return
	}

	// Store result
	h.results[detectionResult.ID] = detectionResult

	c.JSON(http.StatusOK, detectionResult)
}

// callYOLOService sends image to Python YOLO service and returns detections
func (h *VisionHandler) callYOLOService(imageData []byte, filename string) (*DetectionResult, error) {
	// Create multipart request
	body := new(bytes.Buffer)
	writer := multipart.NewWriter(body)

	// Add file field
	part, err := writer.CreateFormFile("file", filename)
	if err != nil {
		return nil, fmt.Errorf("failed to create form file: %v", err)
	}

	_, err = io.Copy(part, bytes.NewReader(imageData))
	if err != nil {
		return nil, fmt.Errorf("failed to write file data: %v", err)
	}

	err = writer.Close()
	if err != nil {
		return nil, fmt.Errorf("failed to close writer: %v", err)
	}

	// Make HTTP request to YOLO service
	url := fmt.Sprintf("%s/detect", h.yoloServiceURL)
	req, err := http.NewRequest("POST", url, body)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to call YOLO service: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("YOLO service returned status %d: %s", resp.StatusCode, string(body))
	}

	// Parse response
	var yoloResp struct {
		ID        string      `json:"id"`
		ImageURL  string      `json:"image_url"`
		Detections []Detection `json:"detections"`
		ModelUsed string      `json:"model_used"`
		CreatedAt string      `json:"created_at"`
	}

	err = json.NewDecoder(resp.Body).Decode(&yoloResp)
	if err != nil {
		return nil, fmt.Errorf("failed to parse YOLO response: %v", err)
	}

	// Create result
	result := &DetectionResult{
		ID:         yoloResp.ID,
		ImageURL:   yoloResp.ImageURL,
		Detections: yoloResp.Detections,
		CreatedAt:  yoloResp.CreatedAt,
	}

	return result, nil
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

// Health check
func (h *VisionHandler) Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":         "ok",
		"service":        "vision-service",
		"yolo_service":   h.yoloServiceURL,
	})
}
