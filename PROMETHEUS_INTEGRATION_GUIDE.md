# Prometheus Monitoring Integration Guide

## 🎯 Overview

This guide explains how to add Prometheus metrics to AgroVision microservices.

## 📊 Prometheus Stack

```
Services (Go)
  ├─ /metrics endpoints
  └─ Prometheus client library
    ↓
Prometheus (Port 9090)
  ├─ Scrapes metrics every 15s
  ├─ TSDB storage (30-day retention)
  └─ Alert rules evaluation
    ↓
Grafana (Port 3000)
  ├─ Visualizes metrics
  ├─ Dashboards
  └─ Alerts notification
```

## 🚀 Integration Steps

### Step 1: Add Prometheus Client to Go Service

```bash
go get github.com/prometheus/client_golang/prometheus
go get github.com/prometheus/client_golang/prometheus/promhttp
```

### Step 2: Define Metrics

```go
package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	// HTTP Metrics
	HTTPRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total HTTP requests",
		},
		[]string{"method", "path", "status"},
	)

	HTTPRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "HTTP request duration",
			Buckets: []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5},
		},
		[]string{"method", "path"},
	)

	// Service Metrics
	DetectionsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "vision_detections_total",
			Help: "Total vision detections processed",
		},
		[]string{"model", "status"},
	)

	DetectionConfidence = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "vision_detection_confidence",
			Help:    "Detection confidence scores",
			Buckets: prometheus.LinearBuckets(0, 0.1, 11),
		},
		[]string{"class"},
	)
)
```

### Step 3: Instrument Middleware

```go
// middleware/metrics.go
package middleware

import (
	"time"
	"github.com/gin-gonic/gin"
	"github.com/agrovision/service/metrics"
)

func MetricsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()

		// Continue processing
		c.Next()

		// Record metrics
		duration := time.Since(start).Seconds()
		status := c.Writer.Status()

		metrics.HTTPRequestsTotal.WithLabelValues(
			c.Request.Method,
			c.Request.URL.Path,
			fmt.Sprintf("%d", status),
		).Inc()

		metrics.HTTPRequestDuration.WithLabelValues(
			c.Request.Method,
			c.Request.URL.Path,
		).Observe(duration)
	}
}
```

### Step 4: Expose /metrics Endpoint

```go
// router/router.go
package router

import (
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	router := gin.New()

	// Prometheus metrics endpoint (public)
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// Add middleware
	router.Use(middleware.MetricsMiddleware())

	// Your routes...

	return router
}
```

### Step 5: Instrument Handlers

```go
// handler/vision.go
package handler

import (
	"github.com/agrovision/service/metrics"
)

func (h *VisionHandler) Detect(c *gin.Context) {
	// Process detection
	detections := h.runYOLO(imageData)

	// Record metrics
	metrics.DetectionsTotal.WithLabelValues("yolov8n", "success").Inc()

	for _, det := range detections {
		metrics.DetectionConfidence.WithLabelValues(det.Class).Observe(det.Confidence)
	}

	c.JSON(200, detections)
}
```

## 📈 Key Metrics to Track

### HTTP Metrics
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) by (job) / sum(rate(http_requests_total[5m])) by (job)

# Latency (p95)
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (job, le))
```

### Vision Service Metrics
```promql
# Detection rate
rate(vision_detections_total[5m])

# Average confidence
avg(vision_detection_confidence)

# Failed detections
sum(rate(vision_detections_total{status="failed"}[5m]))
```

### ML Training Metrics
```promql
# Training jobs
ml_training_status{status="training"}

# Training progress
ml_training_progress

# Average accuracy
avg(ml_training_accuracy)
```

### System Metrics (Docker)
```promql
# Memory usage
container_memory_usage_bytes / 1024 / 1024 / 1024

# CPU usage
rate(container_cpu_usage_seconds_total[5m])

# Network I/O
rate(container_network_receive_bytes_total[5m])
```

## 🎯 Prometheus Config

The `infra/prometheus/prometheus.yml` automatically scrapes all services:

```yaml
scrape_configs:
  - job_name: 'vision-service'
    static_configs:
      - targets: ['vision-service:8003']

  - job_name: 'ml-service'
    static_configs:
      - targets: ['ml-service:8004']

  # ... etc
```

## 📊 Grafana Dashboards

### Create Custom Dashboard

1. Login to Grafana: http://localhost:3000
2. Admin credentials: `admin` / `admin` (from `.env`)
3. **Create → Dashboard**
4. **Add Panel → Choose Prometheus datasource**
5. Write PromQL query
6. Save dashboard

### Useful Panels

**Request Rate**:
```promql
rate(http_requests_total[5m])
```

**Error Rate**:
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) by (job) / sum(rate(http_requests_total[5m])) by (job)
```

**Latency P95**:
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (job, le))
```

**Service Health**:
```promql
up
```

**Memory Usage**:
```promql
container_memory_usage_bytes / 1024 / 1024 / 1024
```

## 🚨 Alerting

Alerts are defined in `infra/prometheus/rules/agrovision_alerts.yml`.

Example alerts:
- Service Down (critical)
- High Error Rate (warning)
- High Latency (warning)
- Memory/CPU Exhaustion (warning)
- DB Connection Pool Exhaustion (critical)
- YOLO Accuracy Drop (warning)

### Testing Alert

```bash
# Trigger alert by stopping a service
docker-compose down vision-service

# Check Prometheus UI: http://localhost:9090/alerts
# Alert should fire after 2 minutes
```

## 🔧 Configuration

### Environment Variables

```bash
# Prometheus
PROMETHEUS_PORT=9090

# Grafana
GRAFANA_PORT=3000
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

### Prometheus Storage

```yaml
# In docker-compose
prometheus:
  command:
    - "--storage.tsdb.path=/prometheus"
    - "--storage.tsdb.retention.time=30d"  # 30-day retention
    - "--web.enable-lifecycle"
```

## 📱 Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Prometheus | http://localhost:9090 | None |
| Grafana | http://localhost:3000 | admin/admin |

## 🔍 Useful Prometheus Queries

### Service Health
```promql
# All services status
up

# Service availability percentage (5m)
avg_over_time(up[5m]) * 100
```

### Performance
```promql
# Top 5 slowest endpoints
topk(5, histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])))

# Request distribution by method
sum(rate(http_requests_total[5m])) by (method)
```

### Errors
```promql
# Error rate by service
sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)

# Status code distribution
sum(rate(http_requests_total[5m])) by (status)
```

### Resource Usage
```promql
# Memory usage (GB)
container_memory_usage_bytes / 1024 / 1024 / 1024

# CPU cores
rate(container_cpu_usage_seconds_total[5m])

# Disk usage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

## 🐛 Troubleshooting

### Prometheus not scraping services

1. Check `prometheus.yml` configuration
2. Verify services have `/metrics` endpoint
3. Check service is running: `docker ps`
4. Check service logs: `docker logs <service>`
5. Test endpoint: `curl http://service:port/metrics`

### Grafana not connecting to Prometheus

1. Verify Prometheus is running: `curl http://prometheus:9090/-/healthy`
2. Check datasource config: Grafana → Configuration → Data Sources
3. Verify URL is correct: `http://prometheus:9090`

### High memory usage

- Check Prometheus retention policy
- Reduce scrape interval
- Remove unnecessary metrics
- Increase container memory limit

## 📚 References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Go Prometheus Client](https://github.com/prometheus/client_golang)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)

## 🎓 Example: Complete Vision Service Integration

```go
// services/vision_service_go/pkg/metrics/metrics.go
package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

func Init() {
	promauto.NewCounter(prometheus.CounterOpts{
		Name: "vision_service_started_total",
		Help: "Total times service has started",
	}).Inc()
}

var (
	VisionDetectionsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "vision_detections_total",
			Help: "Total vision detections",
		},
		[]string{"model", "status"},
	)

	VisionDetectionLatency = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "vision_detection_latency_seconds",
			Help:    "Detection latency",
			Buckets: prometheus.ExponentialBuckets(0.01, 2, 8),
		},
		[]string{"model"},
	)
)

// services/vision_service_go/cmd/main/main.go
package main

import (
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/agrovision/vision-service/pkg/metrics"
)

func main() {
	metrics.Init()
	
	// Expose metrics
	http.HandleFunc("/metrics", promhttp.Handler())
	
	// Start service...
}
```

---

**Status**: ✅ Phase 6.5 - Prometheus Monitoring Ready
**Last Updated**: 2024-05-05
