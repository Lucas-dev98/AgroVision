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
