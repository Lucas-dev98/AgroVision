package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/agrovision/financial-service/internal/models"
	"github.com/google/uuid"
)

type ExpenseRepository struct {
	db *sql.DB
}

func NewExpenseRepository(db *sql.DB) *ExpenseRepository {
	return &ExpenseRepository{db: db}
}

func (r *ExpenseRepository) Create(ctx context.Context, expense *models.Expense) error {
	expense.ID = uuid.NewString()

	const query = `
		INSERT INTO expenses (id, property_id, category, amount, date, description)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING created_at
	`

	err := r.db.QueryRowContext(ctx, query,
		expense.ID,
		expense.PropertyID,
		expense.Category,
		expense.Amount,
		expense.Date,
		expense.Description,
	).Scan(&expense.CreatedAt)
	if err != nil {
		return fmt.Errorf("create expense: %w", err)
	}

	return nil
}

func (r *ExpenseRepository) GetByID(ctx context.Context, id string) (*models.Expense, error) {
	const query = `
		SELECT id, property_id, category, amount, date, description, created_at
		FROM expenses
		WHERE id = $1
	`

	var expense models.Expense
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&expense.ID,
		&expense.PropertyID,
		&expense.Category,
		&expense.Amount,
		&expense.Date,
		&expense.Description,
		&expense.CreatedAt,
	)
	if err == sql.ErrNoRows {
		return nil, models.ErrExpenseNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("get expense by id: %w", err)
	}

	return &expense, nil
}

func (r *ExpenseRepository) ListByPropertyID(ctx context.Context, propertyID string) ([]models.Expense, error) {
	const query = `
		SELECT id, property_id, category, amount, date, description, created_at
		FROM expenses
		WHERE property_id = $1
		ORDER BY date DESC, created_at DESC
	`

	rows, err := r.db.QueryContext(ctx, query, propertyID)
	if err != nil {
		return nil, fmt.Errorf("list expenses by property_id: %w", err)
	}
	defer rows.Close()

	items := make([]models.Expense, 0)
	for rows.Next() {
		var expense models.Expense
		if err := rows.Scan(
			&expense.ID,
			&expense.PropertyID,
			&expense.Category,
			&expense.Amount,
			&expense.Date,
			&expense.Description,
			&expense.CreatedAt,
		); err != nil {
			return nil, fmt.Errorf("scan expense row: %w", err)
		}
		items = append(items, expense)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate expense rows: %w", err)
	}

	return items, nil
}

func (r *ExpenseRepository) SummaryByPropertyID(ctx context.Context, propertyID string) (*models.ExpenseSummary, error) {
	const query = `
		SELECT property_id, COALESCE(SUM(amount), 0), COUNT(*)
		FROM expenses
		WHERE property_id = $1
		GROUP BY property_id
	`

	var summary models.ExpenseSummary
	err := r.db.QueryRowContext(ctx, query, propertyID).Scan(
		&summary.PropertyID,
		&summary.TotalExpenses,
		&summary.ExpenseCount,
	)
	if err == sql.ErrNoRows {
		return &models.ExpenseSummary{PropertyID: propertyID, TotalExpenses: 0, ExpenseCount: 0}, nil
	}
	if err != nil {
		return nil, fmt.Errorf("expense summary by property_id: %w", err)
	}

	return &summary, nil
}

func (r *ExpenseRepository) Update(ctx context.Context, expense *models.Expense) error {
	const query = `
		UPDATE expenses
		SET category = $1,
			amount = $2,
			date = $3,
			description = $4
		WHERE id = $5
	`

	result, err := r.db.ExecContext(ctx, query,
		expense.Category,
		expense.Amount,
		expense.Date,
		expense.Description,
		expense.ID,
	)
	if err != nil {
		return fmt.Errorf("update expense: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("rows affected on update: %w", err)
	}
	if rows == 0 {
		return models.ErrExpenseNotFound
	}

	return nil
}

func (r *ExpenseRepository) Delete(ctx context.Context, id string) error {
	const query = `DELETE FROM expenses WHERE id = $1`

	result, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("delete expense: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("rows affected on delete: %w", err)
	}
	if rows == 0 {
		return models.ErrExpenseNotFound
	}

	return nil
}
