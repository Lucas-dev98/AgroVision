package models

import (
	"errors"
	"strings"
	"time"
)

type Expense struct {
	ID          string    `json:"id"`
	PropertyID  string    `json:"property_id"`
	Category    string    `json:"category"`
	Amount      float64   `json:"amount"`
	Date        time.Time `json:"date"`
	Description string    `json:"description"`
	CreatedAt   time.Time `json:"created_at"`
}

type ExpenseSummary struct {
	PropertyID    string  `json:"property_id"`
	TotalExpenses float64 `json:"total_expenses"`
	ExpenseCount  int     `json:"expense_count"`
}

type CreateExpenseRequest struct {
	PropertyID  string    `json:"property_id"`
	Category    string    `json:"category"`
	Amount      float64   `json:"amount"`
	Date        time.Time `json:"date"`
	Description string    `json:"description"`
}

type UpdateExpenseRequest struct {
	Category    string    `json:"category"`
	Amount      float64   `json:"amount"`
	Date        time.Time `json:"date"`
	Description string    `json:"description"`
}

var (
	ErrPropertyIDRequired   = errors.New("property_id is required")
	ErrCategoryRequired     = errors.New("category is required")
	ErrAmountMustBePositive = errors.New("amount must be greater than 0")
	ErrDateRequired         = errors.New("date is required")
	ErrExpenseNotFound      = errors.New("expense not found")
)

func (r *CreateExpenseRequest) Validate() error {
	r.PropertyID = strings.TrimSpace(r.PropertyID)
	r.Category = strings.TrimSpace(r.Category)
	if r.PropertyID == "" {
		return ErrPropertyIDRequired
	}
	if r.Category == "" {
		return ErrCategoryRequired
	}
	if r.Amount <= 0 {
		return ErrAmountMustBePositive
	}
	if r.Date.IsZero() {
		return ErrDateRequired
	}
	return nil
}

func (r *UpdateExpenseRequest) Validate() error {
	r.Category = strings.TrimSpace(r.Category)
	if r.Category == "" {
		return ErrCategoryRequired
	}
	if r.Amount <= 0 {
		return ErrAmountMustBePositive
	}
	if r.Date.IsZero() {
		return ErrDateRequired
	}
	return nil
}
