package models

import "errors"

type PropertySummaryReport struct {
	PropertyID        string  `json:"property_id"`
	TotalProductionKg float64 `json:"total_production_kg"`
	TotalExpenses     float64 `json:"total_expenses"`
	ExpenseCount      int64   `json:"expense_count"`
	LowStockCount     int64   `json:"low_stock_count"`
}

var ErrPropertyIDRequired = errors.New("property_id is required")
