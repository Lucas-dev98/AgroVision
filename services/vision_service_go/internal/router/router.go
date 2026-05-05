package router
package router

import (
	"github.com/agrovision/vision-service/internal/handler"
	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()

	// Use middleware
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Health check
	visionHandler := handler.NewVisionHandler()
	router.GET("/health", visionHandler.Health)

	// Vision routes
	vision := router.Group("/vision")
	{
		vision.POST("/detect", visionHandler.Detect)
		vision.GET("/results/:id", visionHandler.GetResult)
		vision.GET("/results", visionHandler.ListResults)
	}

	return router
}
