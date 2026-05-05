package router

import (
	"github.com/agrovision/pesagem-service/internal/handler"
	"github.com/agrovision/pesagem-service/internal/middleware"
	"github.com/gin-gonic/gin"
)

func SetupRoutes(r *gin.Engine, pesagemHandler *handler.PesagemHandler) {
	// Health check (no auth)
	r.GET("/health", pesagemHandler.Health)

	// API routes (with auth)
	api := r.Group("/api/v1")
	api.Use(middleware.AuthMiddleware())
	{
		pesagens := api.Group("/pesagens")
		{
			pesagens.GET("", pesagemHandler.GetAll)
			pesagens.GET("/:id", pesagemHandler.GetByID)
			pesagens.GET("/animal/:animalID", pesagemHandler.GetByAnimalID)
			pesagens.GET("/animal/:animalID/latest", pesagemHandler.GetLatestByAnimalID)
			pesagens.POST("", pesagemHandler.Create)
			pesagens.PUT("/:id", pesagemHandler.Update)
			pesagens.DELETE("/:id", pesagemHandler.Delete)
		}
	}
}
