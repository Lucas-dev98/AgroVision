package repository

import (
	"context"
	"database/sql"
	"fmt"
	"sort"
	"sync"
	"time"

	"github.com/agrovision/climate-service/internal/models"
	"github.com/google/uuid"
)

type WeatherAlertRepository struct {
	db     *sql.DB
	mu     sync.RWMutex
	alerts map[string]models.WeatherAlert
}

func NewWeatherAlertRepository(db *sql.DB) *WeatherAlertRepository {
	return &WeatherAlertRepository{
		db:     db,
		alerts: make(map[string]models.WeatherAlert),
	}
}

func (r *WeatherAlertRepository) Create(ctx context.Context, alert *models.WeatherAlert) error {
	if r.db == nil {
		return r.createInMemory(alert)
	}

	alert.ID = uuid.NewString()

	const query = `
		INSERT INTO weather_alerts (id, property_id, alert_type, severity, description, recommended_action)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING created_at, resolved_at
	`

	err := r.db.QueryRowContext(ctx, query,
		alert.ID,
		alert.PropertyID,
		alert.AlertType,
		alert.Severity,
		alert.Description,
		alert.RecommendedAction,
	).Scan(&alert.CreatedAt, &alert.ResolvedAt)
	if err != nil {
		return fmt.Errorf("create weather alert: %w", err)
	}

	return nil
}

func (r *WeatherAlertRepository) GetByID(ctx context.Context, id string) (*models.WeatherAlert, error) {
	if r.db == nil {
		return r.getByIDInMemory(id)
	}

	const query = `
		SELECT id, property_id, alert_type, severity, description, recommended_action, created_at, resolved_at
		FROM weather_alerts
		WHERE id = $1
	`

	var alert models.WeatherAlert
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&alert.ID,
		&alert.PropertyID,
		&alert.AlertType,
		&alert.Severity,
		&alert.Description,
		&alert.RecommendedAction,
		&alert.CreatedAt,
		&alert.ResolvedAt,
	)
	if err == sql.ErrNoRows {
		return nil, models.ErrAlertNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("get weather alert by id: %w", err)
	}

	return &alert, nil
}

func (r *WeatherAlertRepository) ListByPropertyID(ctx context.Context, propertyID string) ([]models.WeatherAlert, error) {
	if r.db == nil {
		return r.listByPropertyIDInMemory(propertyID), nil
	}

	const query = `
		SELECT id, property_id, alert_type, severity, description, recommended_action, created_at, resolved_at
		FROM weather_alerts
		WHERE property_id = $1
		ORDER BY created_at DESC
	`

	rows, err := r.db.QueryContext(ctx, query, propertyID)
	if err != nil {
		return nil, fmt.Errorf("list weather alerts by property_id: %w", err)
	}
	defer rows.Close()

	alerts := make([]models.WeatherAlert, 0)
	for rows.Next() {
		var alert models.WeatherAlert
		err = rows.Scan(
			&alert.ID,
			&alert.PropertyID,
			&alert.AlertType,
			&alert.Severity,
			&alert.Description,
			&alert.RecommendedAction,
			&alert.CreatedAt,
			&alert.ResolvedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scan weather alert row: %w", err)
		}
		alerts = append(alerts, alert)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate weather alert rows: %w", err)
	}

	return alerts, nil
}

func (r *WeatherAlertRepository) Update(ctx context.Context, alert *models.WeatherAlert) error {
	if r.db == nil {
		return r.updateInMemory(alert)
	}

	const query = `
		UPDATE weather_alerts
		SET alert_type = $1,
			severity = $2,
			description = $3,
			recommended_action = $4,
			resolved_at = $5
		WHERE id = $6
	`

	result, err := r.db.ExecContext(ctx, query,
		alert.AlertType,
		alert.Severity,
		alert.Description,
		alert.RecommendedAction,
		alert.ResolvedAt,
		alert.ID,
	)
	if err != nil {
		return fmt.Errorf("update weather alert: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("rows affected on update: %w", err)
	}
	if rows == 0 {
		return models.ErrAlertNotFound
	}

	return nil
}

func (r *WeatherAlertRepository) Delete(ctx context.Context, id string) error {
	if r.db == nil {
		return r.deleteInMemory(id)
	}

	const query = `DELETE FROM weather_alerts WHERE id = $1`

	result, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("delete weather alert: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("rows affected on delete: %w", err)
	}
	if rows == 0 {
		return models.ErrAlertNotFound
	}

	return nil
}

func (r *WeatherAlertRepository) createInMemory(alert *models.WeatherAlert) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now().UTC()
	alert.ID = uuid.NewString()
	alert.CreatedAt = now
	r.alerts[alert.ID] = *alert
	return nil
}

func (r *WeatherAlertRepository) getByIDInMemory(id string) (*models.WeatherAlert, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	alert, ok := r.alerts[id]
	if !ok {
		return nil, models.ErrAlertNotFound
	}
	copy := alert
	return &copy, nil
}

func (r *WeatherAlertRepository) listByPropertyIDInMemory(propertyID string) []models.WeatherAlert {
	r.mu.RLock()
	defer r.mu.RUnlock()

	alerts := make([]models.WeatherAlert, 0)
	for _, alert := range r.alerts {
		if alert.PropertyID == propertyID {
			alerts = append(alerts, alert)
		}
	}

	sort.Slice(alerts, func(i, j int) bool {
		return alerts[i].CreatedAt.After(alerts[j].CreatedAt)
	})

	return alerts
}

func (r *WeatherAlertRepository) updateInMemory(alert *models.WeatherAlert) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	existing, ok := r.alerts[alert.ID]
	if !ok {
		return models.ErrAlertNotFound
	}

	alert.PropertyID = existing.PropertyID
	alert.CreatedAt = existing.CreatedAt
	r.alerts[alert.ID] = *alert
	return nil
}

func (r *WeatherAlertRepository) deleteInMemory(id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, ok := r.alerts[id]; !ok {
		return models.ErrAlertNotFound
	}
	delete(r.alerts, id)
	return nil
}
