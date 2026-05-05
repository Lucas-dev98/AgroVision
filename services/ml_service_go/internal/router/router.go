package router
package router

import (
	"github.com/agrovision/ml-service/internal/db"
	"github.com/agrovision/ml-service/internal/handler"
	"github.com/agrovision/ml-service/internal/middleware"
	"github.com/gin-gonic/gin"
)

func SetupRouter(mongoConnection *db.MongoConnection, jwtSecret string) *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()

	// Use middleware
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Health check (public)
	mlHandler := handler.NewMLHandler(mongoConnection)
	router.GET("/health", mlHandler.Health)

	// Public routes
	public := router.Group("")
	{
		// Models (read-only public)
		public.GET("/ml/models", mlHandler.GetModels)
		public.GET("/ml/models/:id", mlHandler.GetModel)
	}

	// Protected routes (require JWT)
	protected := router.Group("")
	protected.Use(middleware.AuthMiddleware(jwtSecret))
	{
		// Training (requires auth)
		protected.POST("/ml/train", mlHandler.Train)
		protected.GET("/ml/training-history", mlHandler.GetTrainingHistory)
		protected.GET("/ml/training-history/model/:model_id", mlHandler.GetTrainingHistoryByModel)

		// Predictions (requires auth)
		protected.POST("/ml/predict", mlHandler.Predict)
		protected.GET("/ml/predictions", mlHandler.GetPredictionHistory)
		protected.GET("/ml/predictions/:id", mlHandler.GetPrediction)
	}

	return router
}
