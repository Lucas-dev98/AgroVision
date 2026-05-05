package handler

import (
	"net/http"
	"strconv"

	"github.com/agrovision/cotacao-service/internal/models"
	"github.com/agrovision/cotacao-service/internal/service"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type CotacaoHandler struct {
	service service.CotacaoService
	logger  *zap.Logger
}

func NewCotacaoHandler(service service.CotacaoService, logger *zap.Logger) *CotacaoHandler {
	return &CotacaoHandler{
		service: service,
		logger:  logger,
	}
}

// GET /api/v1/cotacoes
func (h *CotacaoHandler) GetAll(c *gin.Context) {
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

	cotacoes, err := h.service.GetAll(c.Request.Context(), limit, offset)
	if err != nil {
		h.logger.Error("Error getting cotacoes", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	if cotacoes == nil {
		cotacoes = []models.Cotacao{}
	}

	count, _ := h.service.Count(c.Request.Context())

	c.JSON(http.StatusOK, gin.H{
		"data":  cotacoes,
		"count": count,
	})
}

// GET /api/v1/cotacoes/:id
func (h *CotacaoHandler) GetByID(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID"})
		return
	}

	cotacao, err := h.service.GetByID(c.Request.Context(), id)
	if err != nil {
		h.logger.Error("Error getting cotacao", zap.Int("id", id), zap.Error(err))
		c.JSON(http.StatusNotFound, gin.H{"error": "Cotacao not found"})
		return
	}

	c.JSON(http.StatusOK, cotacao)
}

// GET /api/v1/cotacoes/tipo/:tipoGado/latest
func (h *CotacaoHandler) GetLatestByTipo(c *gin.Context) {
	tipoGado := c.Param("tipoGado")

	cotacao, err := h.service.GetLatestByTipo(c.Request.Context(), tipoGado)
	if err != nil {
		h.logger.Error("Error getting latest cotacao", zap.String("tipoGado", tipoGado), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	if cotacao == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "No cotacao found"})
		return
	}

	c.JSON(http.StatusOK, cotacao)
}

// GET /api/v1/cotacoes/tipo/:tipoGado
func (h *CotacaoHandler) GetByTipoAndData(c *gin.Context) {
	tipoGado := c.Param("tipoGado")
	dataReferencia := c.Query("data")

	if dataReferencia == "" {
		dataReferencia = "2024-01-01"
	}

	cotacoes, err := h.service.GetByTipoAndData(c.Request.Context(), tipoGado, dataReferencia)
	if err != nil {
		h.logger.Error("Error getting cotacoes", zap.String("tipoGado", tipoGado), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	if cotacoes == nil {
		cotacoes = []models.Cotacao{}
	}

	c.JSON(http.StatusOK, gin.H{"data": cotacoes})
}

// POST /api/v1/cotacoes
func (h *CotacaoHandler) Create(c *gin.Context) {
	var req models.CreateCotacaoRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	cotacao, err := h.service.Create(c.Request.Context(), &req)
	if err != nil {
		h.logger.Error("Error creating cotacao", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create cotacao"})
		return
	}

	c.JSON(http.StatusCreated, cotacao)
}

// PUT /api/v1/cotacoes/:id
func (h *CotacaoHandler) Update(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID"})
		return
	}

	var req models.UpdateCotacaoRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	cotacao, err := h.service.Update(c.Request.Context(), id, &req)
	if err != nil {
		h.logger.Error("Error updating cotacao", zap.Int("id", id), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update cotacao"})
		return
	}

	c.JSON(http.StatusOK, cotacao)
}

// DELETE /api/v1/cotacoes/:id
func (h *CotacaoHandler) Delete(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID"})
		return
	}

	if err := h.service.Delete(c.Request.Context(), id); err != nil {
		h.logger.Error("Error deleting cotacao", zap.Int("id", id), zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete cotacao"})
		return
	}

	c.JSON(http.StatusNoContent, nil)
}

// Health check
func (h *CotacaoHandler) Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
	})
}
