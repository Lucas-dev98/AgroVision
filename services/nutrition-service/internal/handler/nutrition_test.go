package handler

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/agrovision/nutrition-service/internal/repository"
	"github.com/gorilla/mux"
)

func setupRouter() *mux.Router {
	return setupRouterWithAnimalService("")
}

func setupRouterWithAnimalService(animalServiceURL string) *mux.Router {
	repo := repository.NewNutritionRepository(nil)
	h := NewNutritionHandler(repo, animalServiceURL)
	r := mux.NewRouter()
	h.RegisterRoutes(r)
	return r
}

func TestCreateAndListNutrition(t *testing.T) {
	r := setupRouter()

	payload := map[string]any{
		"property_id": "prop-1",
		"animal_id":   "animal-1",
		"feed_type":   "silagem",
		"quantity_kg": 14.2,
		"meal_time":   time.Now().UTC().Format(time.RFC3339),
		"notes":       "manha",
	}
	body, _ := json.Marshal(payload)

	createReq := httptest.NewRequest(http.MethodPost, "/nutrition", bytes.NewReader(body))
	createReq.Header.Set("Content-Type", "application/json")
	createW := httptest.NewRecorder()
	r.ServeHTTP(createW, createReq)

	if createW.Code != http.StatusCreated {
		t.Fatalf("expected 201, got %d body=%s", createW.Code, createW.Body.String())
	}

	listReq := httptest.NewRequest(http.MethodGet, "/nutrition?property_id=prop-1", nil)
	listW := httptest.NewRecorder()
	r.ServeHTTP(listW, listReq)

	if listW.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d body=%s", listW.Code, listW.Body.String())
	}

	var records []map[string]any
	if err := json.Unmarshal(listW.Body.Bytes(), &records); err != nil {
		t.Fatalf("failed to parse list response: %v", err)
	}
	if len(records) != 1 {
		t.Fatalf("expected 1 record, got %d", len(records))
	}
}

func TestListNutritionByAnimal(t *testing.T) {
	r := setupRouter()

	mealTime := time.Now().UTC().Format(time.RFC3339)
	payloads := []map[string]any{
		{
			"property_id": "prop-1",
			"animal_id":   "animal-1",
			"feed_type":   "silagem",
			"quantity_kg": 10.5,
			"meal_time":   mealTime,
		},
		{
			"property_id": "prop-1",
			"animal_id":   "animal-1",
			"feed_type":   "racao",
			"quantity_kg": 5.0,
			"meal_time":   mealTime,
		},
		{
			"property_id": "prop-1",
			"animal_id":   "animal-2",
			"feed_type":   "feno",
			"quantity_kg": 3.0,
			"meal_time":   mealTime,
		},
	}

	for _, payload := range payloads {
		body, _ := json.Marshal(payload)
		req := httptest.NewRequest(http.MethodPost, "/nutrition", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		if w.Code != http.StatusCreated {
			t.Fatalf("expected 201, got %d body=%s", w.Code, w.Body.String())
		}
	}

	historyReq := httptest.NewRequest(http.MethodGet, "/nutrition/animal/animal-1?property_id=prop-1", nil)
	historyW := httptest.NewRecorder()
	r.ServeHTTP(historyW, historyReq)

	if historyW.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d body=%s", historyW.Code, historyW.Body.String())
	}

	var records []map[string]any
	if err := json.Unmarshal(historyW.Body.Bytes(), &records); err != nil {
		t.Fatalf("failed to parse history response: %v", err)
	}
	if len(records) != 2 {
		t.Fatalf("expected 2 records for animal-1, got %d", len(records))
	}
}

func TestUpdateAndDeleteNutrition(t *testing.T) {
	r := setupRouter()

	createPayload := map[string]any{
		"property_id": "prop-1",
		"animal_id":   "animal-1",
		"feed_type":   "silagem",
		"quantity_kg": 9.5,
		"meal_time":   time.Now().UTC().Format(time.RFC3339),
		"notes":       "inicial",
	}
	body, _ := json.Marshal(createPayload)

	createReq := httptest.NewRequest(http.MethodPost, "/nutrition", bytes.NewReader(body))
	createReq.Header.Set("Content-Type", "application/json")
	createW := httptest.NewRecorder()
	r.ServeHTTP(createW, createReq)

	if createW.Code != http.StatusCreated {
		t.Fatalf("expected 201, got %d body=%s", createW.Code, createW.Body.String())
	}

	var created map[string]any
	if err := json.Unmarshal(createW.Body.Bytes(), &created); err != nil {
		t.Fatalf("failed to parse create response: %v", err)
	}
	id, _ := created["id"].(string)
	if id == "" {
		t.Fatalf("expected created id")
	}

	updatePayload := map[string]any{
		"feed_type":   "racao premium",
		"quantity_kg": 11.2,
		"meal_time":   time.Now().UTC().Add(1 * time.Hour).Format(time.RFC3339),
		"notes":       "ajuste",
	}
	updateBody, _ := json.Marshal(updatePayload)

	updateReq := httptest.NewRequest(http.MethodPut, "/nutrition/"+id, bytes.NewReader(updateBody))
	updateReq.Header.Set("Content-Type", "application/json")
	updateW := httptest.NewRecorder()
	r.ServeHTTP(updateW, updateReq)

	if updateW.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d body=%s", updateW.Code, updateW.Body.String())
	}

	deleteReq := httptest.NewRequest(http.MethodDelete, "/nutrition/"+id, nil)
	deleteW := httptest.NewRecorder()
	r.ServeHTTP(deleteW, deleteReq)

	if deleteW.Code != http.StatusNoContent {
		t.Fatalf("expected 204, got %d body=%s", deleteW.Code, deleteW.Body.String())
	}

	getReq := httptest.NewRequest(http.MethodGet, "/nutrition/"+id, nil)
	getW := httptest.NewRecorder()
	r.ServeHTTP(getW, getReq)

	if getW.Code != http.StatusNotFound {
		t.Fatalf("expected 404 after delete, got %d body=%s", getW.Code, getW.Body.String())
	}
}

func TestDailySummaryByPropertyAndAnimal(t *testing.T) {
	r := setupRouter()

	day := "2026-07-01"
	nextDay := "2026-07-02"
	payloads := []map[string]any{
		{
			"property_id": "prop-1",
			"animal_id":   "animal-1",
			"feed_type":   "silagem",
			"quantity_kg": 10.0,
			"meal_time":   day + "T08:00:00Z",
		},
		{
			"property_id": "prop-1",
			"animal_id":   "animal-1",
			"feed_type":   "racao",
			"quantity_kg": 5.0,
			"meal_time":   day + "T12:00:00Z",
		},
		{
			"property_id": "prop-1",
			"animal_id":   "animal-2",
			"feed_type":   "silagem",
			"quantity_kg": 4.0,
			"meal_time":   day + "T09:00:00Z",
		},
		{
			"property_id": "prop-1",
			"animal_id":   "animal-1",
			"feed_type":   "silagem",
			"quantity_kg": 7.0,
			"meal_time":   nextDay + "T08:00:00Z",
		},
		{
			"property_id": "prop-2",
			"animal_id":   "animal-9",
			"feed_type":   "feno",
			"quantity_kg": 3.0,
			"meal_time":   day + "T08:00:00Z",
		},
	}

	for _, payload := range payloads {
		body, _ := json.Marshal(payload)
		req := httptest.NewRequest(http.MethodPost, "/nutrition", bytes.NewReader(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		r.ServeHTTP(w, req)
		if w.Code != http.StatusCreated {
			t.Fatalf("expected 201, got %d body=%s", w.Code, w.Body.String())
		}
	}

	summaryReq := httptest.NewRequest(http.MethodGet, "/nutrition/summary/daily?property_id=prop-1&date="+day, nil)
	summaryW := httptest.NewRecorder()
	r.ServeHTTP(summaryW, summaryReq)

	if summaryW.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d body=%s", summaryW.Code, summaryW.Body.String())
	}

	var summary map[string]any
	if err := json.Unmarshal(summaryW.Body.Bytes(), &summary); err != nil {
		t.Fatalf("failed to parse summary response: %v", err)
	}

	if summary["records_count"].(float64) != 3 {
		t.Fatalf("expected 3 records, got %v", summary["records_count"])
	}
	if summary["total_quantity_kg"].(float64) != 19.0 {
		t.Fatalf("expected total 19.0, got %v", summary["total_quantity_kg"])
	}

	feedType := summary["by_feed_type"].(map[string]any)
	if feedType["silagem"].(float64) != 14.0 {
		t.Fatalf("expected silagem 14.0, got %v", feedType["silagem"])
	}
	if feedType["racao"].(float64) != 5.0 {
		t.Fatalf("expected racao 5.0, got %v", feedType["racao"])
	}

	animalSummaryReq := httptest.NewRequest(http.MethodGet, "/nutrition/summary/daily?property_id=prop-1&animal_id=animal-1&date="+day, nil)
	animalSummaryW := httptest.NewRecorder()
	r.ServeHTTP(animalSummaryW, animalSummaryReq)

	if animalSummaryW.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d body=%s", animalSummaryW.Code, animalSummaryW.Body.String())
	}

	var animalSummary map[string]any
	if err := json.Unmarshal(animalSummaryW.Body.Bytes(), &animalSummary); err != nil {
		t.Fatalf("failed to parse animal summary response: %v", err)
	}

	if animalSummary["records_count"].(float64) != 2 {
		t.Fatalf("expected 2 records for animal-1, got %v", animalSummary["records_count"])
	}
	if animalSummary["total_quantity_kg"].(float64) != 15.0 {
		t.Fatalf("expected total 15.0 for animal-1, got %v", animalSummary["total_quantity_kg"])
	}
}

func TestDailySummaryInvalidDate(t *testing.T) {
	r := setupRouter()

	req := httptest.NewRequest(http.MethodGet, "/nutrition/summary/daily?property_id=prop-1&date=01-07-2026", nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d body=%s", w.Code, w.Body.String())
	}

	var payload map[string]any
	if err := json.Unmarshal(w.Body.Bytes(), &payload); err != nil {
		t.Fatalf("failed to parse error response: %v", err)
	}

	if payload["error"] != "date must be in YYYY-MM-DD format" {
		t.Fatalf("unexpected error message: %v", payload["error"])
	}
}

func TestCreateNutritionInvalidAnimal(t *testing.T) {
	animalService := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/animals/animal-missing" {
			w.WriteHeader(http.StatusNotFound)
			return
		}
		w.WriteHeader(http.StatusOK)
	}))
	defer animalService.Close()

	r := setupRouterWithAnimalService(animalService.URL)

	payload := map[string]any{
		"property_id": "prop-1",
		"animal_id":   "animal-missing",
		"feed_type":   "silagem",
		"quantity_kg": 8.5,
		"meal_time":   time.Now().UTC().Format(time.RFC3339),
	}
	body, _ := json.Marshal(payload)

	req := httptest.NewRequest(http.MethodPost, "/nutrition", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Fatalf("expected 400, got %d body=%s", w.Code, w.Body.String())
	}

	var response map[string]any
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("failed to parse response: %v", err)
	}

	if response["error"] != "animal_id not found" {
		t.Fatalf("unexpected error message: %v", response["error"])
	}
}
