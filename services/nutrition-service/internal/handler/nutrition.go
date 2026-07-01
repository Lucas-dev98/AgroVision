package handler

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/agrovision/nutrition-service/internal/models"
	"github.com/agrovision/nutrition-service/internal/repository"
	"github.com/gorilla/mux"
)

type NutritionHandler struct {
	repo             *repository.NutritionRepository
	animalServiceURL string
	httpClient       *http.Client
}

func NewNutritionHandler(repo *repository.NutritionRepository, animalServiceURL string) *NutritionHandler {
	return &NutritionHandler{
		repo:             repo,
		animalServiceURL: strings.TrimSpace(animalServiceURL),
		httpClient: &http.Client{
			Timeout: 2 * time.Second,
		},
	}
}

func (h *NutritionHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/nutrition", h.CreateNutrition).Methods(http.MethodPost)
	router.HandleFunc("/nutrition", h.ListNutrition).Methods(http.MethodGet)
	router.HandleFunc("/nutrition/summary/daily", h.GetDailySummary).Methods(http.MethodGet)
	router.HandleFunc("/nutrition/animal/{animal_id}", h.ListNutritionByAnimal).Methods(http.MethodGet)
	router.HandleFunc("/nutrition/{id}", h.GetNutrition).Methods(http.MethodGet)
	router.HandleFunc("/nutrition/{id}", h.UpdateNutrition).Methods(http.MethodPut)
	router.HandleFunc("/nutrition/{id}", h.DeleteNutrition).Methods(http.MethodDelete)
}

func (h *NutritionHandler) CreateNutrition(w http.ResponseWriter, r *http.Request) {
	var req models.CreateNutritionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	if req.PropertyID == "" {
		req.PropertyID = strings.TrimSpace(r.Header.Get("X-Property-ID"))
	}
	if req.PropertyID == "" {
		req.PropertyID = strings.TrimSpace(r.URL.Query().Get("property_id"))
	}

	if err := req.Validate(); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	if err := h.validateAnimalID(r.Context(), req.AnimalID); err != nil {
		if errors.Is(err, models.ErrAnimalNotFound) {
			writeError(w, http.StatusBadRequest, err.Error())
			return
		}
		writeError(w, http.StatusBadGateway, "failed to validate animal")
		return
	}

	record := &models.NutritionRecord{
		PropertyID: req.PropertyID,
		AnimalID:   req.AnimalID,
		FeedType:   req.FeedType,
		QuantityKg: req.QuantityKg,
		MealTime:   req.MealTime,
		Notes:      req.Notes,
	}

	if err := h.repo.Create(r.Context(), record); err != nil {
		writeError(w, http.StatusInternalServerError, "failed to create nutrition record")
		return
	}

	writeJSON(w, http.StatusCreated, record)
}

func (h *NutritionHandler) ListNutrition(w http.ResponseWriter, r *http.Request) {
	propertyID := strings.TrimSpace(r.Header.Get("X-Property-ID"))
	if propertyID == "" {
		propertyID = strings.TrimSpace(r.URL.Query().Get("property_id"))
	}
	if propertyID == "" {
		writeError(w, http.StatusBadRequest, models.ErrPropertyIDRequired.Error())
		return
	}

	records, err := h.repo.ListByPropertyID(r.Context(), propertyID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to list nutrition records")
		return
	}

	writeJSON(w, http.StatusOK, records)
}

func (h *NutritionHandler) ListNutritionByAnimal(w http.ResponseWriter, r *http.Request) {
	animalID := strings.TrimSpace(mux.Vars(r)["animal_id"])
	if animalID == "" {
		writeError(w, http.StatusBadRequest, models.ErrAnimalIDRequired.Error())
		return
	}

	propertyID := strings.TrimSpace(r.Header.Get("X-Property-ID"))
	if propertyID == "" {
		propertyID = strings.TrimSpace(r.URL.Query().Get("property_id"))
	}

	records, err := h.repo.ListByAnimalID(r.Context(), animalID, propertyID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to list nutrition records by animal")
		return
	}

	writeJSON(w, http.StatusOK, records)
}

func (h *NutritionHandler) GetDailySummary(w http.ResponseWriter, r *http.Request) {
	propertyID := strings.TrimSpace(r.Header.Get("X-Property-ID"))
	if propertyID == "" {
		propertyID = strings.TrimSpace(r.URL.Query().Get("property_id"))
	}
	if propertyID == "" {
		writeError(w, http.StatusBadRequest, models.ErrPropertyIDRequired.Error())
		return
	}

	animalID := strings.TrimSpace(r.URL.Query().Get("animal_id"))
	dateStr := strings.TrimSpace(r.URL.Query().Get("date"))

	summaryDate := time.Now().UTC()
	if dateStr != "" {
		parsed, err := time.Parse("2006-01-02", dateStr)
		if err != nil {
			writeError(w, http.StatusBadRequest, models.ErrInvalidDateFormat.Error())
			return
		}
		summaryDate = parsed
	}

	summary, err := h.repo.DailySummary(r.Context(), propertyID, animalID, summaryDate)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to build daily summary")
		return
	}

	writeJSON(w, http.StatusOK, summary)
}

func (h *NutritionHandler) GetNutrition(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	record, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrRecordNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve nutrition record")
		return
	}

	writeJSON(w, http.StatusOK, record)
}

func (h *NutritionHandler) UpdateNutrition(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	current, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrRecordNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve nutrition record")
		return
	}

	var req models.UpdateNutritionRequest
	if err = json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	if err = req.Validate(); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	current.FeedType = req.FeedType
	current.QuantityKg = req.QuantityKg
	current.MealTime = req.MealTime
	current.Notes = req.Notes

	if err = h.validateAnimalID(r.Context(), current.AnimalID); err != nil {
		if errors.Is(err, models.ErrAnimalNotFound) {
			writeError(w, http.StatusBadRequest, err.Error())
			return
		}
		writeError(w, http.StatusBadGateway, "failed to validate animal")
		return
	}

	if err = h.repo.Update(r.Context(), current); err != nil {
		if errors.Is(err, models.ErrRecordNotFound) {
			writeError(w, http.StatusNotFound, err.Error())
			return
		}
		writeError(w, http.StatusInternalServerError, "failed to update nutrition record")
		return
	}

	writeJSON(w, http.StatusOK, current)
}

func (h *NutritionHandler) DeleteNutrition(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	err := h.repo.Delete(r.Context(), id)
	if errors.Is(err, models.ErrRecordNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to delete nutrition record")
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}

func (h *NutritionHandler) validateAnimalID(ctx context.Context, animalID string) error {
	animalID = strings.TrimSpace(animalID)
	if animalID == "" {
		return nil
	}
	if h.animalServiceURL == "" {
		return nil
	}

	baseURL, err := url.Parse(h.animalServiceURL)
	if err != nil {
		return fmt.Errorf("invalid ANIMAL_SERVICE_URL: %w", err)
	}

	targetURL := strings.TrimSuffix(baseURL.String(), "/") + "/animals/" + url.PathEscape(animalID)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, targetURL, nil)
	if err != nil {
		return fmt.Errorf("create animal validation request: %w", err)
	}

	resp, err := h.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("animal validation request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return models.ErrAnimalNotFound
	}
	if resp.StatusCode >= 500 {
		return fmt.Errorf("animal service unavailable: status=%d", resp.StatusCode)
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("animal validation rejected: status=%d", resp.StatusCode)
	}

	return nil
}
