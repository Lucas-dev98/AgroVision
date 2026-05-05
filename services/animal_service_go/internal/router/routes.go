package router

import (
	"github.com/agrovision/animal-service/internal/handler"
	"github.com/agrovision/animal-service/internal/middleware"
	"github.com/gin-gonic/gin"
)

func SetupRoutes(r *gin.Engine, animalHandler *handler.AnimalHandler) {
	// Health check (no auth)
	r.GET("/health", animalHandler.Health)

	// API routes (with auth)
	api := r.Group("/api/v1")
	api.Use(middleware.AuthMiddleware())
	{
		animals := api.Group("/animals")
		{
			animals.GET("", animalHandler.GetAll)
			animals.GET("/:id", animalHandler.GetByID)
			animals.GET("/ear-tag/:earTag", animalHandler.GetByEarTag)
			animals.POST("", animalHandler.Create)
			animals.PUT("/:id", animalHandler.Update)
			animals.DELETE("/:id", animalHandler.Delete)
		}
	}
}
