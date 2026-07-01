package repository

import (
	"context"
	"database/sql"
	"fmt"
	"sort"
	"sync"
	"time"

	"github.com/agrovision/financial-service/internal/models"
	"github.com/google/uuid"
)

type ExpenseRepository struct {
	db    *sql.DB
	mu    sync.RWMutex
	items map[string]models.Expense
}

func NewExpenseRepository(db *sql.DB) *ExpenseRepository {
	return &ExpenseRepository{
		db:    db,
		items: make(map[string]models.Expense),
	}
}

func (r *ExpenseRepository) Create(ctx context.Context, expense *models.Expense) error {
	if r.db == nil {
		return r.createInMemory(expense)
	}

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
	if r.db == nil {
		return r.getByIDInMemory(id)
	}

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
	if r.db == nil {
		return r.listByPropertyIDInMemory(propertyID), nil
	}

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
	if r.db == nil {
		return r.summaryByPropertyIDInMemory(propertyID), nil
	}

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
	if r.db == nil {
		return r.updateInMemory(expense)
	}

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
	if r.db == nil {
		return r.deleteInMemory(id)
	}

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

func (r *ExpenseRepository) createInMemory(expense *models.Expense) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	expense.ID = uuid.NewString()
	expense.CreatedAt = time.Now().UTC()
	r.items[expense.ID] = *expense
	return nil
}

func (r *ExpenseRepository) getByIDInMemory(id string) (*models.Expense, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	expense, ok := r.items[id]
	if !ok {
		return nil, models.ErrExpenseNotFound
	}
	copy := expense
	return &copy, nil
}

func (r *ExpenseRepository) listByPropertyIDInMemory(propertyID string) []models.Expense {
	r.mu.RLock()
	defer r.mu.RUnlock()

	items := make([]models.Expense, 0)
	for _, item := range r.items {
		if item.PropertyID == propertyID {
			items = append(items, item)
		}
	}

	sort.Slice(items, func(i, j int) bool {
		if items[i].Date.Equal(items[j].Date) {
			return items[i].CreatedAt.After(items[j].CreatedAt)
		}
		return items[i].Date.After(items[j].Date)
	})

	return items
}

func (r *ExpenseRepository) summaryByPropertyIDInMemory(propertyID string) *models.ExpenseSummary {
	r.mu.RLock()
	defer r.mu.RUnlock()

	summary := &models.ExpenseSummary{PropertyID: propertyID}
	for _, item := range r.items {
		if item.PropertyID == propertyID {
			summary.TotalExpenses += item.Amount
			summary.ExpenseCount++
		}
	}

	return summary
}

func (r *ExpenseRepository) updateInMemory(expense *models.Expense) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	existing, ok := r.items[expense.ID]
	if !ok {
		return models.ErrExpenseNotFound
	}

	expense.PropertyID = existing.PropertyID
	expense.CreatedAt = existing.CreatedAt
	r.items[expense.ID] = *expense
	return nil
}

func (r *ExpenseRepository) deleteInMemory(id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, ok := r.items[id]; !ok {
		return models.ErrExpenseNotFound
	}

	delete(r.items, id)
	return nil
}
