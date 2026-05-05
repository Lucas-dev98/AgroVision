package router
package router

import (
	"agrovision/vision-service/internal/db"
	"agrovision/vision-service/internal/handler"
	"github.com/gin-gonic/gin"
)

func SetupRouter(mongoConn *db.MongoConnection) *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()

	// Use middleware
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Health check
	visionHandler := handler.NewVisionHandler(mongoConn)
	router.GET("/health", visionHandler.Health)

	// Vision routes
	vision := router.Group("/vision")
	{
		vision.POST("/detect", visionHandler.Detect)
		vision.GET("/results/:id", visionHandler.GetResult)
		vision.GET("/results", visionHandler.ListResults)

		// History endpoints (MongoDB-backed)
		vision.GET("/history", visionHandler.ListHistory)
		vision.GET("/history/:id", visionHandler.GetHistory)
		vision.DELETE("/history/:id", visionHandler.DeleteHistory)
		vision.GET("/search", visionHandler.SearchByClass)
		vision.GET("/statistics", visionHandler.GetStatistics)
	}

	return router
}
