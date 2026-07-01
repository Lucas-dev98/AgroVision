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
	repo := repository.NewNutritionRepository()
	h := NewNutritionHandler(repo)
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
