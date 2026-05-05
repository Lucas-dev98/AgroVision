package router

import (
	"github.com/agrovision/cotacao-service/internal/handler"
	"github.com/agrovision/cotacao-service/internal/middleware"
	"github.com/gin-gonic/gin"
)

func SetupRoutes(r *gin.Engine, cotacaoHandler *handler.CotacaoHandler) {
	// Health check (no auth)
	r.GET("/health", cotacaoHandler.Health)

	// API routes (with auth)
	api := r.Group("/api/v1")
	api.Use(middleware.AuthMiddleware())
	{
		cotacoes := api.Group("/cotacoes")
		{
			cotacoes.GET("", cotacaoHandler.GetAll)
			cotacoes.GET("/:id", cotacaoHandler.GetByID)
			cotacoes.GET("/tipo/:tipoGado", cotacaoHandler.GetByTipoAndData)
			cotacoes.GET("/tipo/:tipoGado/latest", cotacaoHandler.GetLatestByTipo)
			cotacoes.POST("", cotacaoHandler.Create)
			cotacoes.PUT("/:id", cotacaoHandler.Update)
			cotacoes.DELETE("/:id", cotacaoHandler.Delete)
		}
	}
}
