package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strings"

	"github.com/agrovision/stock-service/internal/models"
	"github.com/agrovision/stock-service/internal/repository"
	"github.com/gorilla/mux"
)

type StockHandler struct {
	repo *repository.StockRepository
}

func NewStockHandler(repo *repository.StockRepository) *StockHandler {
	return &StockHandler{repo: repo}
}

func (h *StockHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/stocks/low", h.ListLowStock).Methods(http.MethodGet)
	router.HandleFunc("/stocks", h.CreateStock).Methods(http.MethodPost)
	router.HandleFunc("/stocks", h.ListStocks).Methods(http.MethodGet)
	router.HandleFunc("/stocks/{id}", h.GetStock).Methods(http.MethodGet)
	router.HandleFunc("/stocks/{id}", h.UpdateStock).Methods(http.MethodPut)
	router.HandleFunc("/stocks/{id}", h.DeleteStock).Methods(http.MethodDelete)
}

func (h *StockHandler) CreateStock(w http.ResponseWriter, r *http.Request) {
	var req models.CreateStockRequest
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

	item := &models.StockItem{
		PropertyID:      req.PropertyID,
		ItemName:        req.ItemName,
		Category:        req.Category,
		Quantity:        req.Quantity,
		Unit:            req.Unit,
		MinimumQuantity: req.MinimumQuantity,
		ExpiryDate:      req.ExpiryDate,
	}

	if err := h.repo.Create(r.Context(), item); err != nil {
		writeError(w, http.StatusInternalServerError, "failed to create stock item")
		return
	}

	writeJSON(w, http.StatusCreated, item)
}

func (h *StockHandler) ListStocks(w http.ResponseWriter, r *http.Request) {
	propertyID := strings.TrimSpace(r.Header.Get("X-Property-ID"))
	if propertyID == "" {
		propertyID = strings.TrimSpace(r.URL.Query().Get("property_id"))
	}
	if propertyID == "" {
		writeError(w, http.StatusBadRequest, models.ErrPropertyIDRequired.Error())
		return
	}

	items, err := h.repo.ListByPropertyID(r.Context(), propertyID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to list stock items")
		return
	}

	writeJSON(w, http.StatusOK, items)
}

func (h *StockHandler) ListLowStock(w http.ResponseWriter, r *http.Request) {
	propertyID := strings.TrimSpace(r.Header.Get("X-Property-ID"))
	if propertyID == "" {
		propertyID = strings.TrimSpace(r.URL.Query().Get("property_id"))
	}
	if propertyID == "" {
		writeError(w, http.StatusBadRequest, models.ErrPropertyIDRequired.Error())
		return
	}

	items, err := h.repo.ListLowStockByPropertyID(r.Context(), propertyID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to list low stock items")
		return
	}

	writeJSON(w, http.StatusOK, items)
}

func (h *StockHandler) GetStock(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	item, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrStockNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve stock item")
		return
	}

	writeJSON(w, http.StatusOK, item)
}

func (h *StockHandler) UpdateStock(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	current, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrStockNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve stock item")
		return
	}

	var req models.UpdateStockRequest
	if err = json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	if err = req.Validate(); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	current.ItemName = req.ItemName
	current.Category = req.Category
	current.Quantity = req.Quantity
	current.Unit = req.Unit
	current.MinimumQuantity = req.MinimumQuantity
	current.ExpiryDate = req.ExpiryDate

	if err = h.repo.Update(r.Context(), current); err != nil {
		if errors.Is(err, models.ErrStockNotFound) {
			writeError(w, http.StatusNotFound, err.Error())
			return
		}
		writeError(w, http.StatusInternalServerError, "failed to update stock item")
		return
	}

	writeJSON(w, http.StatusOK, current)
}

func (h *StockHandler) DeleteStock(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	err := h.repo.Delete(r.Context(), id)
	if errors.Is(err, models.ErrStockNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to delete stock item")
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
