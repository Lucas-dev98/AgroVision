package repository

import (
	"context"
	"database/sql"
	"fmt"
	"sort"
	"sync"
	"time"

	"github.com/agrovision/stock-service/internal/models"
	"github.com/google/uuid"
)

type StockRepository struct {
	db    *sql.DB
	mu    sync.RWMutex
	items map[string]models.StockItem
}

func NewStockRepository(db *sql.DB) *StockRepository {
	return &StockRepository{
		db:    db,
		items: make(map[string]models.StockItem),
	}
}

func (r *StockRepository) Create(ctx context.Context, item *models.StockItem) error {
	if r.db == nil {
		return r.createInMemory(item)
	}

	item.ID = uuid.NewString()

	const query = `
		INSERT INTO stock (id, property_id, item_name, category, quantity, unit, minimum_quantity, expiry_date)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		RETURNING created_at, last_updated
	`

	err := r.db.QueryRowContext(ctx, query,
		item.ID,
		item.PropertyID,
		item.ItemName,
		item.Category,
		item.Quantity,
		item.Unit,
		item.MinimumQuantity,
		item.ExpiryDate,
	).Scan(&item.CreatedAt, &item.UpdatedAt)
	if err != nil {
		return fmt.Errorf("create stock item: %w", err)
	}

	return nil
}

func (r *StockRepository) GetByID(ctx context.Context, id string) (*models.StockItem, error) {
	if r.db == nil {
		return r.getByIDInMemory(id)
	}

	const query = `
		SELECT id, property_id, item_name, category, quantity, unit, minimum_quantity, expiry_date, created_at, last_updated
		FROM stock
		WHERE id = $1
	`

	var item models.StockItem
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&item.ID,
		&item.PropertyID,
		&item.ItemName,
		&item.Category,
		&item.Quantity,
		&item.Unit,
		&item.MinimumQuantity,
		&item.ExpiryDate,
		&item.CreatedAt,
		&item.UpdatedAt,
	)
	if err == sql.ErrNoRows {
		return nil, models.ErrStockNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("get stock item by id: %w", err)
	}

	return &item, nil
}

func (r *StockRepository) ListByPropertyID(ctx context.Context, propertyID string) ([]models.StockItem, error) {
	if r.db == nil {
		return r.listByPropertyIDInMemory(propertyID), nil
	}

	const query = `
		SELECT id, property_id, item_name, category, quantity, unit, minimum_quantity, expiry_date, created_at, last_updated
		FROM stock
		WHERE property_id = $1
		ORDER BY last_updated DESC
	`

	rows, err := r.db.QueryContext(ctx, query, propertyID)
	if err != nil {
		return nil, fmt.Errorf("list stock by property_id: %w", err)
	}
	defer rows.Close()

	items := make([]models.StockItem, 0)
	for rows.Next() {
		var item models.StockItem
		err = rows.Scan(
			&item.ID,
			&item.PropertyID,
			&item.ItemName,
			&item.Category,
			&item.Quantity,
			&item.Unit,
			&item.MinimumQuantity,
			&item.ExpiryDate,
			&item.CreatedAt,
			&item.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scan stock row: %w", err)
		}
		items = append(items, item)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate stock rows: %w", err)
	}

	return items, nil
}

func (r *StockRepository) ListLowStockByPropertyID(ctx context.Context, propertyID string) ([]models.StockItem, error) {
	if r.db == nil {
		items := r.listByPropertyIDInMemory(propertyID)
		low := make([]models.StockItem, 0)
		for _, item := range items {
			if item.Quantity <= item.MinimumQuantity {
				low = append(low, item)
			}
		}
		return low, nil
	}

	const query = `
		SELECT id, property_id, item_name, category, quantity, unit, minimum_quantity, expiry_date, created_at, last_updated
		FROM stock
		WHERE property_id = $1
		  AND quantity <= minimum_quantity
		ORDER BY last_updated DESC
	`

	rows, err := r.db.QueryContext(ctx, query, propertyID)
	if err != nil {
		return nil, fmt.Errorf("list low stock by property_id: %w", err)
	}
	defer rows.Close()

	items := make([]models.StockItem, 0)
	for rows.Next() {
		var item models.StockItem
		err = rows.Scan(
			&item.ID,
			&item.PropertyID,
			&item.ItemName,
			&item.Category,
			&item.Quantity,
			&item.Unit,
			&item.MinimumQuantity,
			&item.ExpiryDate,
			&item.CreatedAt,
			&item.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scan low stock row: %w", err)
		}
		items = append(items, item)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate low stock rows: %w", err)
	}

	return items, nil
}

func (r *StockRepository) Update(ctx context.Context, item *models.StockItem) error {
	if r.db == nil {
		return r.updateInMemory(item)
	}

	const query = `
		UPDATE stock
		SET item_name = $1,
			category = $2,
			quantity = $3,
			unit = $4,
			minimum_quantity = $5,
			expiry_date = $6,
			last_updated = NOW()
		WHERE id = $7
		RETURNING last_updated
	`

	err := r.db.QueryRowContext(ctx, query,
		item.ItemName,
		item.Category,
		item.Quantity,
		item.Unit,
		item.MinimumQuantity,
		item.ExpiryDate,
		item.ID,
	).Scan(&item.UpdatedAt)
	if err == sql.ErrNoRows {
		return models.ErrStockNotFound
	}
	if err != nil {
		return fmt.Errorf("update stock item: %w", err)
	}

	return nil
}

func (r *StockRepository) Delete(ctx context.Context, id string) error {
	if r.db == nil {
		return r.deleteInMemory(id)
	}

	const query = `DELETE FROM stock WHERE id = $1`

	result, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("delete stock item: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("rows affected on delete: %w", err)
	}
	if rows == 0 {
		return models.ErrStockNotFound
	}

	return nil
}

func (r *StockRepository) createInMemory(item *models.StockItem) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now().UTC()
	item.ID = uuid.NewString()
	item.CreatedAt = now
	item.UpdatedAt = now
	r.items[item.ID] = *item
	return nil
}

func (r *StockRepository) getByIDInMemory(id string) (*models.StockItem, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	item, ok := r.items[id]
	if !ok {
		return nil, models.ErrStockNotFound
	}
	copy := item
	return &copy, nil
}

func (r *StockRepository) listByPropertyIDInMemory(propertyID string) []models.StockItem {
	r.mu.RLock()
	defer r.mu.RUnlock()

	items := make([]models.StockItem, 0)
	for _, item := range r.items {
		if item.PropertyID == propertyID {
			items = append(items, item)
		}
	}

	sort.Slice(items, func(i, j int) bool {
		return items[i].UpdatedAt.After(items[j].UpdatedAt)
	})

	return items
}

func (r *StockRepository) updateInMemory(item *models.StockItem) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	existing, ok := r.items[item.ID]
	if !ok {
		return models.ErrStockNotFound
	}

	item.PropertyID = existing.PropertyID
	item.CreatedAt = existing.CreatedAt
	item.UpdatedAt = time.Now().UTC()
	r.items[item.ID] = *item
	return nil
}

func (r *StockRepository) deleteInMemory(id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, ok := r.items[id]; !ok {
		return models.ErrStockNotFound
	}
	delete(r.items, id)
	return nil
}
