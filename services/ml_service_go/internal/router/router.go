package router
package router

import (
	"github.com/agrovision/ml-service/internal/handler"
	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()

	// Use middleware
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Health check
	mlHandler := handler.NewMLHandler()
	router.GET("/health", mlHandler.Health)

	// ML routes
	ml := router.Group("/ml")
	{
		// Models
		ml.GET("/models", mlHandler.GetModels)
		ml.GET("/models/:id", mlHandler.GetModel)

		// Training
		ml.POST("/train", mlHandler.Train)

		// Predictions
		ml.POST("/predict", mlHandler.Predict)
		ml.GET("/predictions", mlHandler.GetPredictions)
		ml.GET("/predictions/:id", mlHandler.GetPrediction)
	}

	return router
}
