package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strings"

	"github.com/agrovision/financial-service/internal/models"
	"github.com/agrovision/financial-service/internal/repository"
	"github.com/gorilla/mux"
)

type ExpenseHandler struct {
	repo *repository.ExpenseRepository
}

func NewExpenseHandler(repo *repository.ExpenseRepository) *ExpenseHandler {
	return &ExpenseHandler{repo: repo}
}

func (h *ExpenseHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/expenses", h.CreateExpense).Methods(http.MethodPost)
	router.HandleFunc("/expenses", h.ListExpenses).Methods(http.MethodGet)
	router.HandleFunc("/expenses/summary", h.GetExpenseSummary).Methods(http.MethodGet)
	router.HandleFunc("/expenses/{id}", h.GetExpense).Methods(http.MethodGet)
	router.HandleFunc("/expenses/{id}", h.UpdateExpense).Methods(http.MethodPut)
	router.HandleFunc("/expenses/{id}", h.DeleteExpense).Methods(http.MethodDelete)
}

func (h *ExpenseHandler) CreateExpense(w http.ResponseWriter, r *http.Request) {
	var req models.CreateExpenseRequest
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

	expense := &models.Expense{
		PropertyID:  req.PropertyID,
		Category:    req.Category,
		Amount:      req.Amount,
		Date:        req.Date,
		Description: req.Description,
	}

	if err := h.repo.Create(r.Context(), expense); err != nil {
		writeError(w, http.StatusInternalServerError, "failed to create expense")
		return
	}

	writeJSON(w, http.StatusCreated, expense)
}

func (h *ExpenseHandler) ListExpenses(w http.ResponseWriter, r *http.Request) {
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
		writeError(w, http.StatusInternalServerError, "failed to list expenses")
		return
	}

	writeJSON(w, http.StatusOK, items)
}

func (h *ExpenseHandler) GetExpenseSummary(w http.ResponseWriter, r *http.Request) {
	propertyID := strings.TrimSpace(r.Header.Get("X-Property-ID"))
	if propertyID == "" {
		propertyID = strings.TrimSpace(r.URL.Query().Get("property_id"))
	}
	if propertyID == "" {
		writeError(w, http.StatusBadRequest, models.ErrPropertyIDRequired.Error())
		return
	}

	summary, err := h.repo.SummaryByPropertyID(r.Context(), propertyID)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve expense summary")
		return
	}

	writeJSON(w, http.StatusOK, summary)
}

func (h *ExpenseHandler) GetExpense(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	expense, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrExpenseNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve expense")
		return
	}

	writeJSON(w, http.StatusOK, expense)
}

func (h *ExpenseHandler) UpdateExpense(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	current, err := h.repo.GetByID(r.Context(), id)
	if errors.Is(err, models.ErrExpenseNotFound) {
		writeError(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		writeError(w, http.StatusInternalServerError, "failed to retrieve expense")
		return
	}

	var req models.UpdateExpenseRequest
	if err = json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid request body")
		return
	}
	if err = req.Validate(); err != nil {
		writeError(w, http.StatusBadRequest, err.Error())
		return
	}

	current.Category = req.Category
	current.Amount = req.Amount
	current.Date = req.Date
	current.Description = req.Description

	if err = h.repo.Update(r.Context(), current); err != nil {
		if errors.Is(err, models.ErrExpenseNotFound) {
			writeError(w, http.StatusNotFound, err.Error())
			return
		}
		writeError(w, http.StatusInternalServerError, "failed to update expense")
		return
	}

	writeJSON(w, http.StatusOK, current)
}

func (h *ExpenseHandler) DeleteExpense(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimSpace(mux.Vars(r)["id"])
	if id == "" {
		writeError(w, http.StatusBadRequest, "id is required")
		return
	}

	if err := h.repo.Delete(r.Context(), id); err != nil {
		if errors.Is(err, models.ErrExpenseNotFound) {
			writeError(w, http.StatusNotFound, err.Error())
			return
		}
		writeError(w, http.StatusInternalServerError, "failed to delete expense")
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
