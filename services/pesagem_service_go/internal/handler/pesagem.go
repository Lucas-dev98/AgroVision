package handler

import (
	"net/http"
	"strconv"

	"github.com/agrovision/pesagem-service/internal/models"
	"github.com/agrovision/pesagem-service/internal/service"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type PesagemHandler struct {
	service service.PesagemService
	logger  *zap.Logger
}

func NewPesagemHandler(service service.PesagemService, logger *zap.Logger) *PesagemHandler {
	return &PesagemHandler{
		service: service,
		logger:  logger,
	}
}

// GET /api/v1/pesagens
func (h *PesagemHandler) GetAll(c *gin.Context) {
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

	pesagens, err := h.service.GetAll(c.Request.Context(), limit, offset)
	if err != nil {
		h.logger.Error("Error getting pesagens", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	if pesagens == nil {
		pesagens = []models.Pesagem{}
	}

	count, _ := h.service.Count(c.Request.Context())

	c.JSON(http.StatusOK, gin.H{
		"data":  pesagens,
		"count": count,
	})
}

// GET /api/v1/pesagens/:id
func (h *PesagemHandler) GetByID(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID"})
		return
	}

	pesagem, err := h.service.GetByID(c.Request.Context(), id)
	if err != nil {
		h.logger.Error("Error getting pesagem", zap.Int("id", id), zap.Error(err))
		c.JSON(http.StatusNotFound, gin.H{"error": "Pesagem not found"})
		return
	}

	c.JSON(http.StatusOK, pesagem)
}

// GET /api/v1/pesagens/animal/:animalID
func (h *PesagemHandler) GetByAnimalID(c *gin.Context) {
	animalID, err := strconv.Atoi(c.Param("animalID"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid animal ID"})
		return
	}

	pesagens, err := h.service.GetByAnimalID(c.Request.Context(), animalID)
	if err != nil {
		h.logger.Error("Error getting pesagens by animal ID", zap.Int("animalID", animalID), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	if pesagens == nil {
		pesagens = []models.Pesagem{}
	}

	c.JSON(http.StatusOK, gin.H{"data": pesagens})
}

// GET /api/v1/pesagens/animal/:animalID/latest
func (h *PesagemHandler) GetLatestByAnimalID(c *gin.Context) {
	animalID, err := strconv.Atoi(c.Param("animalID"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid animal ID"})
		return
	}

	pesagem, err := h.service.GetLatestByAnimalID(c.Request.Context(), animalID)
	if err != nil {
		h.logger.Error("Error getting latest pesagem", zap.Int("animalID", animalID), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	if pesagem == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "No pesagem found"})
		return
	}

	c.JSON(http.StatusOK, pesagem)
}

// POST /api/v1/pesagens
func (h *PesagemHandler) Create(c *gin.Context) {
	var req models.CreatePesagemRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	pesagem, err := h.service.Create(c.Request.Context(), &req)
	if err != nil {
		h.logger.Error("Error creating pesagem", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create pesagem"})
		return
	}

	c.JSON(http.StatusCreated, pesagem)
}

// PUT /api/v1/pesagens/:id
func (h *PesagemHandler) Update(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID"})
		return
	}

	var req models.UpdatePesagemRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	pesagem, err := h.service.Update(c.Request.Context(), id, &req)
	if err != nil {
		h.logger.Error("Error updating pesagem", zap.Int("id", id), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update pesagem"})
		return
	}

	c.JSON(http.StatusOK, pesagem)
}

// DELETE /api/v1/pesagens/:id
func (h *PesagemHandler) Delete(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID"})
		return
	}

	if err := h.service.Delete(c.Request.Context(), id); err != nil {
		h.logger.Error("Error deleting pesagem", zap.Int("id", id), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete pesagem"})
		return
	}

	c.JSON(http.StatusNoContent, nil)
}

// Health check
func (h *PesagemHandler) Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
	})
}
