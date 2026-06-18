package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strings"

	"github.com/agrovision/production-service/internal/models"
	"github.com/agrovision/production-service/internal/repository"
	"github.com/gorilla/mux"
)

type ProductionHandler struct {
	repo *repository.ProductionRepository
}

func NewProductionHandler(repo *repository.ProductionRepository) *ProductionHandler {
	return &ProductionHandler{repo: repo}
}

func (h *ProductionHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/productions", h.CreateProduction).Methods(http.MethodPost)
	router.HandleFunc("/productions", h.ListProductions).Methods(http.MethodGet)
	router.HandleFunc("/productions/{id}", h.GetProduction).Methods(http.MethodGet)
	router.HandleFunc("/productions/{id}", h.UpdateProduction).Methods(http.MethodPut)
	router.HandleFunc("/productions/{id}", h.DeleteProduction).Methods(http.MethodDelete)
}

func (h *ProductionHandler) CreateProduction(w http.ResponseWriter, r *http.Request) {
	var req models.CreateProductionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	if req.PlotID == "" {
		req.PlotID = strings.TrimSpace(r.Header.Get("X-Plot-ID"))
	}
	if req.PlotID == "" {
		req.PlotID = strings.TrimSpace(r.URL.Query().Get("plot_id"))
	}

	if err := req.Validate(); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	production := &models.Production{
		PlotID:       req.PlotID,
		HarvestDate:  req.HarvestDate,
		QuantityKg:   req.QuantityKg,
		QualityGrade: req.QualityGrade,
		Notes:        req.Notes,
	}

	if err := h.repo.Create(r.Context(), production); err != nil {
		writeError(w, http.StatusInternalServerError, "failed to create production")
		return
	}

	writeJSON(w, http.StatusCreated, production)
}

func (h *ProductionHandler) ListProductions(w http.ResponseWriter, r *http.Request) {
	plotID := strings.TrimSpace(r.Header.Get("X-Plot-ID"))
	if plotID == "" {
		plotID = strings.TrimSpace(r.URL.Query().Get("plot_id"))
	}
	if plotID == "" {
		writeError(w, http.StatusBadRequest, models.ErrPlotIDRequired.Error())
		return
	}

	items, err := h.repo.ListByPlotID(r.Context(), plotID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to list productions")
		return
	}

	writeJSON(w, http.StatusOK, items)
}

func (h *ProductionHandler) GetProduction(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	production, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrProductionNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve production")
		return
	}

	writeJSON(w, http.StatusOK, production)
}

func (h *ProductionHandler) UpdateProduction(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	current, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrProductionNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve production")
		return
	}

	var req models.UpdateProductionRequest
	if err = json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	if err = req.Validate(); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	current.HarvestDate = req.HarvestDate
	current.QuantityKg = req.QuantityKg
	current.QualityGrade = req.QualityGrade
	current.Notes = req.Notes

	if err = h.repo.Update(r.Context(), current); err != nil {
		if errors.Is(err, models.ErrProductionNotFound) {
			writeError(w, http.StatusNotFound, err.Error())
			return
		}
		writeError(w, http.StatusInternalServerError, "failed to update production")
		return
	}

	writeJSON(w, http.StatusOK, current)
}

func (h *ProductionHandler) DeleteProduction(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	if err := h.repo.Delete(r.Context(), id); err != nil {
		if errors.Is(err, models.ErrProductionNotFound) {
			writeError(w, http.StatusNotFound, err.Error())
			return
		}
		writeError(w, http.StatusInternalServerError, "failed to delete production")
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
