package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/agrovision/reports-service/internal/models"
)

type ReportRepository struct {
	db *sql.DB
}

func NewReportRepository(db *sql.DB) *ReportRepository {
	return &ReportRepository{db: db}
}

func (r *ReportRepository) PropertySummary(ctx context.Context, propertyID string) (*models.PropertySummaryReport, error) {
	if r.db == nil {
		return &models.PropertySummaryReport{
			PropertyID:        propertyID,
			TotalProductionKg: 0,
			TotalExpenses:     0,
			ExpenseCount:      0,
			LowStockCount:     0,
		}, nil
	}

	report := &models.PropertySummaryReport{PropertyID: propertyID}

	const productionQuery = `
		SELECT COALESCE(SUM(p.quantity_kg), 0)
		FROM production p
		JOIN plots pl ON pl.id = p.plot_id
		WHERE pl.property_id = $1
	`
	if err := r.db.QueryRowContext(ctx, productionQuery, propertyID).Scan(&report.TotalProductionKg); err != nil {
		return nil, fmt.Errorf("query production summary: %w", err)
	}

	const expenseQuery = `
		SELECT COALESCE(SUM(amount), 0), COUNT(*)
		FROM expenses
		WHERE property_id = $1
	`
	if err := r.db.QueryRowContext(ctx, expenseQuery, propertyID).Scan(&report.TotalExpenses, &report.ExpenseCount); err != nil {
		return nil, fmt.Errorf("query expense summary: %w", err)
	}

	const lowStockQuery = `
		SELECT COUNT(*)
		FROM stock
		WHERE property_id = $1
		  AND quantity <= minimum_quantity
	`
	if err := r.db.QueryRowContext(ctx, lowStockQuery, propertyID).Scan(&report.LowStockCount); err != nil {
		return nil, fmt.Errorf("query low stock summary: %w", err)
	}

	return report, nil
}
