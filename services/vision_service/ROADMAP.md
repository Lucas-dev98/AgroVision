# 🚀 Vision Service - Development Roadmap

Complete TDD roadmap for Vision Service with 40+ tests across 5 phases.

## 📊 Roadmap Overview

```
PHASE 1: Core Detection  ████████████████████ 12 tests ✅
PHASE 2: Tracking       ░░░░░░░░░░░░░░░░░░░░ 13 tests (in progress)
PHASE 3: Endpoints      ░░░░░░░░░░░░░░░░░░░░ 15 tests (next)
PHASE 4: Integration    ░░░░░░░░░░░░░░░░░░░░ 8 tests
PHASE 5: Optimization   ░░░░░░░░░░░░░░░░░░░░ 5+ tests

TOTAL ESTIMATED: 50+ tests with 100% coverage
```

---

## ✅ PHASE 1: Core Detection Service (12 tests)

**Status**: COMPLETE ✅

### Components

1. **YOLODetectionService**
   - [x] Frame decoding (base64 → numpy array)
   - [x] Frame encoding (numpy array → base64)
   - [x] Object detection with YOLO
   - [x] Trough classification (empty/full)
   - [x] Bounding box normalization (absolute → 0-1)
   - [x] Complete frame processing pipeline

### Tests (12 total)

1. `test_decode_frame_valid` - Decode valid base64 frames ✅
2. `test_decode_frame_invalid` - Handle invalid base64 ✅
3. `test_encode_frame` - Encode numpy array to base64 ✅
4. `test_classify_trough_status_empty` - Empty trough detection ✅
5. `test_classify_trough_status_full` - Full trough detection ✅
6. `test_detect_objects_empty_frame` - No objects in frame ✅
7. `test_detect_objects_with_detections` - Multiple objects ✅
8. `test_process_frame_success` - Complete frame processing ✅
9. `test_process_frame_invalid_data` - Handle bad frames ✅
10. `test_normalize_bbox_coordinates` - Bbox normalization ✅
11. `test_model_initialization` - YOLO model loads ✅
12. `test_animal_count_from_confidence` - Animal counting logic ✅

### Key Files

- `app/services/detection.py` - YOLO detection service
- `app/schemas.py` - Data schemas (Detection, FrameDetectionResult, etc)
- `tests/test_detection_service.py` - Detection tests

---

## ⏳ PHASE 2: MongoDB Repositories (13 tests)

**Status**: IN PROGRESS 🔄

### Components

1. **DetectionRepository**
   - [x] Create detection document
   - [x] Get by frame ID
   - [x] Get by camera with pagination
   - [x] Get recent detections
   - [x] Count animals by camera

2. **AnimalLocationRepository**
   - [x] Create location record
   - [x] Get animal history
   - [x] Get latest locations
   - [x] Count unique animals

3. **CameraCalibrationRepository**
   - [x] Create or update calibration
   - [x] Get by camera ID
   - [x] Update existing
   - [x] Get all calibrations

### Tests (13 total)

**DetectionRepository** (6 tests):
1. `test_create_detection` - Insert detection document ✅
2. `test_get_by_frame_id` - Query by frame ✅
3. `test_get_by_camera` - Query by camera with pagination ✅
4. `test_get_recent` - Query recent detections ✅
5. `test_count_animals_by_camera` - Aggregation query ✅
6. (bonus) Batch insert performance

**AnimalLocationRepository** (5 tests):
1. `test_create_location` - Insert location ✅
2. `test_get_animal_history` - Query history ✅
3. `test_get_latest_locations` - Latest location aggregation ✅
4. `test_count_unique_animals` - Distinct query ✅
5. (bonus) Time-series query optimization

**CameraCalibrationRepository** (4 tests):
1. `test_create_or_update_new` - Insert new calibration ✅
2. `test_get_by_camera_id` - Query calibration ✅
3. `test_update_existing` - Update logic ✅
4. `test_get_all` - Get all calibrations ✅

### Key Files

- `app/models.py` - MongoDB document models
- `app/repositories/__init__.py` - All repository classes
- `app/core/database.py` - MongoDB connection
- `tests/test_repositories.py` - Repository tests

---

## ⏭️ PHASE 3: API Endpoints (15 tests)

**Status**: NEXT 🎯

### Components

1. **Health Check Endpoint**
   - [ ] GET /health - Service status
   - [ ] MongoDB connectivity check
   - [ ] YOLO model status
   - [ ] Timestamp and version

2. **Detection Endpoints**
   - [ ] POST /api/v1/vision/detect - Process frame
   - [ ] GET /api/v1/vision/animals - List detected animals
   - [ ] GET /api/v1/vision/troughs - Trough status

3. **Tracking Endpoints**
   - [ ] GET /api/v1/vision/animals/{id}/history - Animal history
   - [ ] GET /api/v1/vision/animals/latest - Latest locations

4. **Camera Endpoints**
   - [ ] POST /api/v1/vision/cameras/calibrate - Calibrate
   - [ ] GET /api/v1/vision/cameras/{id} - Camera info
   - [ ] GET /api/v1/vision/cameras - List cameras

### Tests (15 total)

**Health** (2 tests):
1. `test_health_check_returns_healthy`
2. `test_health_check_models_loaded`

**Detection** (5 tests):
1. `test_process_frame_success`
2. `test_process_frame_invalid_base64`
3. `test_get_animals_detected`
4. `test_get_trough_status`
5. `test_frame_processing_stores_in_mongodb`

**Tracking** (3 tests):
1. `test_get_animal_history`
2. `test_get_latest_locations`
3. `test_animal_not_found_returns_empty`

**Camera** (4 tests):
1. `test_calibrate_camera`
2. `test_get_camera_info`
3. `test_list_cameras`
4. `test_camera_not_found_returns_404`

**Error Handling** (1 test):
1. `test_mongodb_error_returns_500`

### Key Files

- `main.py` - FastAPI application with all endpoints
- `tests/test_endpoints.py` - Endpoint integration tests

---

## ⏳ PHASE 4: API Gateway Integration (8 tests)

**Status**: PENDING 📋

### Components

1. **Proxy Configuration**
   - [ ] /api/v1/vision/* → Vision Service (8003)
   - [ ] Timeout handling
   - [ ] Error forwarding

2. **Request/Response Validation**
   - [ ] Request schema validation
   - [ ] Response schema matching
   - [ ] Error response format

3. **Authentication Integration**
   - [ ] JWT token validation
   - [ ] Permission checks
   - [ ] Rate limiting per user

### Tests (8 total)

1. `test_api_gateway_proxy_vision_endpoints`
2. `test_vision_endpoint_timeout_handling`
3. `test_invalid_jwt_returns_401`
4. `test_rate_limiting_enforced`
5. `test_response_schema_valid`
6. `test_error_response_format`
7. `test_cors_headers_present`
8. `test_health_check_not_rate_limited`

### Key Files

- `docker-compose.yml` - Add vision_service container
- `services/api_gateway/app/api/routers/vision.py` - Proxy routes
- `tests/test_api_gateway_vision_integration.py` - Integration tests

---

## ⏳ PHASE 5: Performance Optimization (5+ tests)

**Status**: PENDING 📋

### Components

1. **Caching**
   - [ ] Cache detection results (5min TTL)
   - [ ] Cache camera calibrations
   - [ ] Invalidate on updates

2. **Query Optimization**
   - [ ] Index optimization
   - [ ] Query plan analysis
   - [ ] Aggregate pipeline tuning

3. **Batch Processing**
   - [ ] Batch frame processing
   - [ ] Bulk inserts
   - [ ] Async operations

### Tests (5+ total)

1. `test_detection_caching_works`
2. `test_cache_invalidation_on_new_detection`
3. `test_index_on_timestamp_improves_query`
4. `test_batch_frame_processing`
5. `test_bulk_location_insert`
6. (bonus) `test_memory_usage_under_load`
7. (bonus) `test_cpu_usage_optimization`

### Key Files

- `app/core/cache.py` - Redis caching layer
- `app/services/batch_processor.py` - Batch processing
- `tests/test_performance.py` - Performance tests

---

## 📋 Test Execution Commands

```bash
# Run all tests
pytest tests/ -v --cov=app --cov-report=html

# Run specific phase
pytest tests/test_detection_service.py -v              # Phase 1
pytest tests/test_repositories.py -v                   # Phase 2
pytest tests/test_endpoints.py -v                      # Phase 3
pytest tests/test_api_gateway_vision_integration.py -v # Phase 4
pytest tests/test_performance.py -v                    # Phase 5

# Watch mode
pytest-watch tests/ --clear

# Coverage report
pytest --cov=app --cov-report=term-missing
```

## 📊 Coverage Targets

| Component | Target | Status |
|-----------|--------|--------|
| YOLODetectionService | 100% | ✅ |
| DetectionRepository | 100% | ✅ |
| AnimalLocationRepository | 100% | ✅ |
| CameraCalibrationRepository | 100% | ✅ |
| API Endpoints | 100% | ⏳ |
| MongoDB Integration | 100% | ✅ |
| Error Handling | 100% | ⏳ |
| **Overall** | **100%** | **🎯** |

## 🔄 Development Workflow

For each phase:

```
1. Write all tests first (RED phase)
2. Run tests - all fail
3. Implement code (GREEN phase)
4. Run tests - all pass
5. Refactor code
6. Commit: "feat(vision): PHASE X with N tests"
```

## 🎯 Success Criteria

- [x] All tests pass (PHASE 1 ✅)
- [x] 100% code coverage for PHASE 1 ✅
- [ ] All PHASE 2 tests passing (in progress)
- [ ] All PHASE 3 tests passing (next)
- [ ] All PHASE 4 tests passing (pending)
- [ ] All PHASE 5 tests passing (pending)
- [ ] **Total: 50+ tests passing**
- [ ] **100% test coverage**
- [ ] **Zero code without tests**

## 📈 Progress Tracking

```
Week 1: PHASE 1 & 2 ✅
Week 2: PHASE 3 ⏳
Week 3: PHASE 4 & 5
Week 4: Optimization & Documentation
```

---

**Last Updated**: 2026-04-16
**Current Phase**: 2 (MongoDB Repositories)
**Tests Implemented**: 12
**Tests Pending**: 38+
