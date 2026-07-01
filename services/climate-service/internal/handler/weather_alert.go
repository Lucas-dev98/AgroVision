package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strings"

	"github.com/agrovision/climate-service/internal/models"
	"github.com/agrovision/climate-service/internal/repository"
	"github.com/gorilla/mux"
)

type WeatherAlertHandler struct {
	repo *repository.WeatherAlertRepository
}

func NewWeatherAlertHandler(repo *repository.WeatherAlertRepository) *WeatherAlertHandler {
	return &WeatherAlertHandler{repo: repo}
}

func (h *WeatherAlertHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/weather-alerts", h.CreateWeatherAlert).Methods(http.MethodPost)
	router.HandleFunc("/weather-alerts", h.ListWeatherAlerts).Methods(http.MethodGet)
	router.HandleFunc("/weather-alerts/{id}", h.GetWeatherAlert).Methods(http.MethodGet)
	router.HandleFunc("/weather-alerts/{id}", h.UpdateWeatherAlert).Methods(http.MethodPut)
	router.HandleFunc("/weather-alerts/{id}", h.DeleteWeatherAlert).Methods(http.MethodDelete)
}

func (h *WeatherAlertHandler) CreateWeatherAlert(w http.ResponseWriter, r *http.Request) {
	var req models.CreateWeatherAlertRequest
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

	alert := &models.WeatherAlert{
		PropertyID:        req.PropertyID,
		AlertType:         req.AlertType,
		Severity:          req.Severity,
		Description:       req.Description,
		RecommendedAction: req.RecommendedAction,
	}

	if err := h.repo.Create(r.Context(), alert); err != nil {
		writeError(w, http.StatusInternalServerError, "failed to create weather alert")
		return
	}

	writeJSON(w, http.StatusCreated, alert)
}

func (h *WeatherAlertHandler) ListWeatherAlerts(w http.ResponseWriter, r *http.Request) {
	propertyID := strings.TrimSpace(r.Header.Get("X-Property-ID"))
	if propertyID == "" {
		propertyID = strings.TrimSpace(r.URL.Query().Get("property_id"))
	}
	if propertyID == "" {
		writeError(w, http.StatusBadRequest, models.ErrPropertyIDRequired.Error())
		return
	}

	alerts, err := h.repo.ListByPropertyID(r.Context(), propertyID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to list weather alerts")
		return
	}

	writeJSON(w, http.StatusOK, alerts)
}

func (h *WeatherAlertHandler) GetWeatherAlert(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	alert, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrAlertNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve weather alert")
		return
	}

	writeJSON(w, http.StatusOK, alert)
}

func (h *WeatherAlertHandler) UpdateWeatherAlert(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	current, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrAlertNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve weather alert")
		return
	}

	var req models.UpdateWeatherAlertRequest
	if err = json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	if err = req.Validate(); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	current.AlertType = req.AlertType
	current.Severity = req.Severity
	current.Description = req.Description
	current.RecommendedAction = req.RecommendedAction
	current.ResolvedAt = req.ResolvedAt

	if err = h.repo.Update(r.Context(), current); err != nil {
		if errors.Is(err, models.ErrAlertNotFound) {
			writeError(w, http.StatusNotFound, err.Error())
			return
		}
		writeError(w, http.StatusInternalServerError, "failed to update weather alert")
		return
	}

	writeJSON(w, http.StatusOK, current)
}

func (h *WeatherAlertHandler) DeleteWeatherAlert(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	err := h.repo.Delete(r.Context(), id)
	if errors.Is(err, models.ErrAlertNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to delete weather alert")
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
