package handler

import (
	"net/http"
	"strconv"

	"github.com/agrovision/animal-service/internal/models"
	"github.com/agrovision/animal-service/internal/service"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type AnimalHandler struct {
	service service.AnimalService
	logger  *zap.Logger
}

func NewAnimalHandler(service service.AnimalService, logger *zap.Logger) *AnimalHandler {
	return &AnimalHandler{
		service: service,
		logger:  logger,
	}
}

// GET /api/v1/animals
func (h *AnimalHandler) GetAll(c *gin.Context) {
	limit := 10
	offset := 0

	if l := c.Query("limit"); l != "" {
		if parsed, err := strconv.Atoi(l); err == nil {
			limit = parsed
		}
	}

	if o := c.Query("offset"); o != "" {
		if parsed, err := strconv.Atoi(o); err == nil {
			offset = parsed
		}
	}

	animals, err := h.service.GetAll(c.Request.Context(), limit, offset)
	if err != nil {
		h.logger.Error("Error getting animals", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	if animals == nil {
		animals = []models.Animal{}
	}

	count, _ := h.service.Count(c.Request.Context())

	c.JSON(http.StatusOK, gin.H{
		"data":  animals,
		"count": count,
	})
}

// GET /api/v1/animals/:id
func (h *AnimalHandler) GetByID(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID"})
		return
	}

	animal, err := h.service.GetByID(c.Request.Context(), id)
	if err != nil {
		h.logger.Error("Error getting animal", zap.Int("id", id), zap.Error(err))
		c.JSON(http.StatusNotFound, gin.H{"error": "Animal not found"})
		return
	}

	c.JSON(http.StatusOK, animal)
}

// GET /api/v1/animals/ear-tag/:earTag
func (h *AnimalHandler) GetByEarTag(c *gin.Context) {
	earTag := c.Param("earTag")

	animal, err := h.service.GetByEarTag(c.Request.Context(), earTag)
	if err != nil {
		h.logger.Error("Error getting animal by ear tag", zap.String("earTag", earTag), zap.Error(err))
		c.JSON(http.StatusNotFound, gin.H{"error": "Animal not found"})
		return
	}

	c.JSON(http.StatusOK, animal)
}

// POST /api/v1/animals
func (h *AnimalHandler) Create(c *gin.Context) {
	var req models.CreateAnimalRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	animal, err := h.service.Create(c.Request.Context(), &req)
	if err != nil {
		h.logger.Error("Error creating animal", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create animal"})
		return
	}

	c.JSON(http.StatusCreated, animal)
}

// PUT /api/v1/animals/:id
func (h *AnimalHandler) Update(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID"})
		return
	}

	var req models.UpdateAnimalRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	animal, err := h.service.Update(c.Request.Context(), id, &req)
	if err != nil {
		h.logger.Error("Error updating animal", zap.Int("id", id), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update animal"})
		return
	}

	c.JSON(http.StatusOK, animal)
}

// DELETE /api/v1/animals/:id
func (h *AnimalHandler) Delete(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID"})
		return
	}

	if err := h.service.Delete(c.Request.Context(), id); err != nil {
		h.logger.Error("Error deleting animal", zap.Int("id", id), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete animal"})
		return
	}

	c.JSON(http.StatusNoContent, nil)
}

// Health check
func (h *AnimalHandler) Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
	})
}
