package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strings"

	"github.com/agrovision/nutrition-service/internal/models"
	"github.com/agrovision/nutrition-service/internal/repository"
	"github.com/gorilla/mux"
)

type NutritionHandler struct {
	repo *repository.NutritionRepository
}

func NewNutritionHandler(repo *repository.NutritionRepository) *NutritionHandler {
	return &NutritionHandler{repo: repo}
}

func (h *NutritionHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/nutrition", h.CreateNutrition).Methods(http.MethodPost)
	router.HandleFunc("/nutrition", h.ListNutrition).Methods(http.MethodGet)
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
