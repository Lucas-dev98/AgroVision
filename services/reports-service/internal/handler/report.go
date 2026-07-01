package handler

import (
	"encoding/json"
	"net/http"
	"strings"

	"github.com/agrovision/reports-service/internal/models"
	"github.com/agrovision/reports-service/internal/repository"
	"github.com/gorilla/mux"
)

type ReportHandler struct {
	repo *repository.ReportRepository
}

func NewReportHandler(repo *repository.ReportRepository) *ReportHandler {
	return &ReportHandler{repo: repo}
}

func (h *ReportHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/reports/property-summary", h.PropertySummary).Methods(http.MethodGet)
}

func (h *ReportHandler) PropertySummary(w http.ResponseWriter, r *http.Request) {
	propertyID := strings.TrimSpace(r.Header.Get("X-Property-ID"))
	if propertyID == "" {
		propertyID = strings.TrimSpace(r.URL.Query().Get("property_id"))
	}
	if propertyID == "" {
		writeError(w, http.StatusBadRequest, models.ErrPropertyIDRequired.Error())
		return
	}

	report, err := h.repo.PropertySummary(r.Context(), propertyID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to build property summary report")
		return
	}

	writeJSON(w, http.StatusOK, report)
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}
