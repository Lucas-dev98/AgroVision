package router

import (
	"github.com/agrovision/api-gateway/internal/config"
	"github.com/agrovision/api-gateway/internal/handler"
	"github.com/agrovision/api-gateway/internal/middleware"
	"github.com/agrovision/api-gateway/internal/proxy"
	"github.com/gin-gonic/gin"
)

func SetupRouter(cfg *config.Config) *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()

	// Add middleware
	router.Use(middleware.CORSMiddleware())
	router.Use(middleware.LoggingMiddleware(cfg.Logger))
	router.Use(middleware.ErrorHandlingMiddleware(cfg.Logger))
	router.Use(middleware.HeaderMiddleware())

	// Rate limiting middleware
	rateLimiterCfg := middleware.RateLimitConfig{
		RequestsPerWindow: cfg.RateLimitRequests,
		Window:            cfg.RateLimitWindow,
	}
	rateLimiter := middleware.NewRateLimiter(rateLimiterCfg, cfg.Logger)
	router.Use(rateLimiter.Middleware())

	// Create proxy
	proxyConfig := proxy.ProxyConfig{
		AnimalServiceURL:  cfg.AnimalServiceURL,
		PesagemServiceURL: cfg.PesagemServiceURL,
		CotacaoServiceURL: cfg.CotacaoServiceURL,
		VisionServiceURL:  cfg.VisionServiceURL,
		MLServiceURL:      cfg.MLServiceURL,
		Logger:            cfg.Logger,
	}
	proxyHandler := proxy.NewProxy(proxyConfig)

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "ok",
			"service": "api-gateway",
		})
	})

	// API v1 routes
	apiV1 := router.Group("/api/v1")

	// Authentication routes (no middleware required)
	authHandler := handler.NewAuthHandler()
	auth := apiV1.Group("/auth")
	{
		auth.POST("/login", authHandler.Login)
		auth.POST("/logout", authHandler.Logout)
		auth.POST("/refresh", authHandler.Refresh)
		auth.GET("/profile", middleware.AuthMiddleware(), authHandler.GetProfile)
	}

	// Protect all other routes with authentication middleware
	apiV1.Use(middleware.AuthMiddleware())

	// Animal routes
	animals := apiV1.Group("/animals")
	{
		animals.GET("", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		animals.GET("/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		animals.POST("", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		animals.PUT("/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		animals.DELETE("/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
	}

	// Pesagem routes
	pesagens := apiV1.Group("/pesagens")
	{
		pesagens.GET("", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		pesagens.GET("/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		pesagens.POST("", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		pesagens.PUT("/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		pesagens.DELETE("/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
	}

	// Cotacao routes
	cotacoes := apiV1.Group("/cotacoes")
	{
		cotacoes.GET("", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		cotacoes.GET("/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		cotacoes.POST("", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		cotacoes.PUT("/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		cotacoes.DELETE("/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
	}

	// Vision routes
	vision := apiV1.Group("/vision")
	{
		vision.POST("/detect", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		vision.GET("/results/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
	}

	// ML routes
	ml := apiV1.Group("/ml")
	{
		ml.GET("/models", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		ml.GET("/models/:id", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		ml.POST("/predict", func(c *gin.Context) { proxyHandler.RouteToService(c) })
		ml.POST("/train", func(c *gin.Context) { proxyHandler.RouteToService(c) })
	}

	// Catch-all route for any other paths
	router.NoRoute(func(c *gin.Context) {
		proxyHandler.RouteToService(c)
	})

	cfg.Logger.Info("Router setup complete")

	return router
}
