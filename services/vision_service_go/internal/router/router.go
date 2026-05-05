package router
package router

import (
	"agrovision/vision-service/internal/db"
	"agrovision/vision-service/internal/handler"
	"agrovision/vision-service/internal/middleware"
	"github.com/gin-gonic/gin"
)

func SetupRouter(mongoConn *db.MongoConnection) *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()

	// Use middleware
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Health check (no auth required)
	visionHandler := handler.NewVisionHandler(mongoConn)
	router.GET("/health", visionHandler.Health)

	// Public vision routes (optional auth)
	publicVision := router.Group("/vision")
	publicVision.Use(middleware.OptionalAuthMiddleware())
	{
		publicVision.GET("/results/:id", visionHandler.GetResult)
		publicVision.GET("/results", visionHandler.ListResults)
	}

	// Protected vision routes (JWT required)
	protectedVision := router.Group("/vision")
	protectedVision.Use(middleware.AuthMiddleware())
	{
		protectedVision.POST("/detect", visionHandler.Detect)
		protectedVision.GET("/history", visionHandler.ListHistory)
		protectedVision.GET("/history/:id", visionHandler.GetHistory)
		protectedVision.DELETE("/history/:id", visionHandler.DeleteHistory)
		protectedVision.GET("/search", visionHandler.SearchByClass)
		protectedVision.GET("/statistics", visionHandler.GetStatistics)
	}

	return router
}
