package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strings"

	"github.com/agrovision/property-service/internal/models"
	"github.com/agrovision/property-service/internal/repository"
	"github.com/gorilla/mux"
)

type PropertyHandler struct {
	repo *repository.PropertyRepository
}

func NewPropertyHandler(repo *repository.PropertyRepository) *PropertyHandler {
	return &PropertyHandler{repo: repo}
}

func (h *PropertyHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/properties", h.CreateProperty).Methods(http.MethodPost)
	router.HandleFunc("/properties", h.ListProperties).Methods(http.MethodGet)
	router.HandleFunc("/properties/{id}", h.GetProperty).Methods(http.MethodGet)
	router.HandleFunc("/properties/{id}", h.UpdateProperty).Methods(http.MethodPut)
	router.HandleFunc("/properties/{id}", h.DeleteProperty).Methods(http.MethodDelete)
}

func (h *PropertyHandler) CreateProperty(w http.ResponseWriter, r *http.Request) {
	var req models.CreatePropertyRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	if req.UserID == "" {
		req.UserID = strings.TrimSpace(r.Header.Get("X-User-ID"))
	}
	if req.UserID == "" {
		req.UserID = strings.TrimSpace(r.URL.Query().Get("user_id"))
	}

	if err := req.Validate(); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	prop := &models.Property{
		UserID:      req.UserID,
		Name:        req.Name,
		TotalArea:   req.TotalArea,
		PlantedArea: req.PlantedArea,
		LocationLat: req.LocationLat,
		LocationLng: req.LocationLng,
		SoilType:    req.SoilType,
	}

	if err := h.repo.Create(r.Context(), prop); err != nil {
		writeError(w, http.StatusInternalServerError, "failed to create property")
		return
	}

	writeJSON(w, http.StatusCreated, prop)
}

func (h *PropertyHandler) ListProperties(w http.ResponseWriter, r *http.Request) {
	userID := strings.TrimSpace(r.Header.Get("X-User-ID"))
	if userID == "" {
		userID = strings.TrimSpace(r.URL.Query().Get("user_id"))
	}
	if userID == "" {
		writeError(w, http.StatusBadRequest, models.ErrUserIDRequired.Error())
		return
	}

	properties, err := h.repo.ListByUserID(r.Context(), userID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to list properties")
		return
	}

	writeJSON(w, http.StatusOK, properties)
}

func (h *PropertyHandler) GetProperty(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	prop, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrPropertyNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve property")
		return
	}

	writeJSON(w, http.StatusOK, prop)
}

func (h *PropertyHandler) UpdateProperty(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	current, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrPropertyNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve property")
		return
	}

	var req models.UpdatePropertyRequest
	if err = json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	if err = req.Validate(); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	current.Name = req.Name
	current.TotalArea = req.TotalArea
	current.PlantedArea = req.PlantedArea
	current.LocationLat = req.LocationLat
	current.LocationLng = req.LocationLng
	current.SoilType = req.SoilType

	if err = h.repo.Update(r.Context(), current); err != nil {
		if errors.Is(err, models.ErrPropertyNotFound) {
			writeError(w, http.StatusNotFound, err.Error())
			return
		}
		writeError(w, http.StatusInternalServerError, "failed to update property")
		return
	}

	writeJSON(w, http.StatusOK, current)
}

func (h *PropertyHandler) DeleteProperty(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	err := h.repo.Delete(r.Context(), id)
	if errors.Is(err, models.ErrPropertyNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to delete property")
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
