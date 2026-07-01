package repository

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"time"

	"github.com/agrovision/api-gateway/internal/models"
)

type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{db: db}
}

// Create creates a new user
func (r *UserRepository) Create(user *models.User) error {
	if r.db == nil {
		return errors.New("database not configured")
	}

	query := `
		INSERT INTO users (username, email, password_hash, full_name, role, is_active, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
		RETURNING id, created_at, updated_at
	`

	err := r.db.QueryRow(
		query,
		user.Username,
		user.Email,
		user.PasswordHash,
		user.FullName,
		user.Role,
		user.IsActive,
	).Scan(&user.ID, &user.CreatedAt, &user.UpdatedAt)

	if err != nil {
		if err.Error() == "pq: duplicate key value violates unique constraint \"users_username_key\"" {
			return fmt.Errorf("username already exists")
		}
		if err.Error() == "pq: duplicate key value violates unique constraint \"users_email_key\"" {
			return fmt.Errorf("email already exists")
		}
		return err
	}

	return nil
}

// GetByID gets a user by ID
func (r *UserRepository) GetByID(id int) (*models.User, error) {
	user := &models.User{}
	query := `
		SELECT id, username, email, password_hash, full_name, role, is_active, created_at, updated_at
		FROM users
		WHERE id = $1
	`

	err := r.db.QueryRow(query, id).Scan(
		&user.ID,
		&user.Username,
		&user.Email,
		&user.PasswordHash,
		&user.FullName,
		&user.Role,
		&user.IsActive,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, errors.New("user not found")
	}
	if err != nil {
		return nil, err
	}

	return user, nil
}

// GetByUsername gets a user by username
func (r *UserRepository) GetByUsername(username string) (*models.User, error) {
	if r.db == nil {
		return nil, errors.New("database not configured")
	}

	user := &models.User{}
	query := `
		SELECT id, username, email, password_hash, full_name, role, is_active, created_at, updated_at
		FROM users
		WHERE username = $1 AND is_active = true
	`

	err := r.db.QueryRow(query, username).Scan(
		&user.ID,
		&user.Username,
		&user.Email,
		&user.PasswordHash,
		&user.FullName,
		&user.Role,
		&user.IsActive,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, errors.New("user not found")
	}
	if err != nil {
		return nil, err
	}

	return user, nil
}

// GetByEmail gets a user by email
func (r *UserRepository) GetByEmail(email string) (*models.User, error) {
	user := &models.User{}
	query := `
		SELECT id, username, email, password_hash, full_name, role, is_active, created_at, updated_at
		FROM users
		WHERE email = $1 AND is_active = true
	`

	err := r.db.QueryRow(query, email).Scan(
		&user.ID,
		&user.Username,
		&user.Email,
		&user.PasswordHash,
		&user.FullName,
		&user.Role,
		&user.IsActive,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, errors.New("user not found")
	}
	if err != nil {
		return nil, err
	}

	return user, nil
}

// Update updates a user
func (r *UserRepository) Update(id int, updates *models.UserUpdate) error {
	query := `
		UPDATE users
		SET email = COALESCE($1, email),
		    full_name = COALESCE($2, full_name),
		    role = COALESCE($3, role),
		    is_active = $4,
		    updated_at = NOW()
		WHERE id = $5
	`

	result, err := r.db.Exec(query, updates.Email, updates.FullName, updates.Role, updates.IsActive, id)
	if err != nil {
		return err
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rows == 0 {
		return errors.New("user not found")
	}

	return nil
}

// Delete soft-deletes a user (sets is_active to false)
func (r *UserRepository) Delete(id int) error {
	query := `
		UPDATE users
		SET is_active = false,
		    updated_at = NOW()
		WHERE id = $1
	`

	result, err := r.db.Exec(query, id)
	if err != nil {
		return err
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rows == 0 {
		return errors.New("user not found")
	}

	return nil
}

// ListAll gets all active users
func (r *UserRepository) ListAll() ([]*models.User, error) {
	query := `
		SELECT id, username, email, password_hash, full_name, role, is_active, created_at, updated_at
		FROM users
		WHERE is_active = true
		ORDER BY created_at DESC
	`

	rows, err := r.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var users []*models.User
	for rows.Next() {
		user := &models.User{}
		err := rows.Scan(
			&user.ID,
			&user.Username,
			&user.Email,
			&user.PasswordHash,
			&user.FullName,
			&user.Role,
			&user.IsActive,
			&user.CreatedAt,
			&user.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		users = append(users, user)
	}

	return users, rows.Err()
}

// UpdatePassword updates a user's password hash
func (r *UserRepository) UpdatePassword(id int, passwordHash string) error {
	query := `
		UPDATE users
		SET password_hash = $1,
		    updated_at = NOW()
		WHERE id = $2
	`

	result, err := r.db.Exec(query, passwordHash, id)
	if err != nil {
		return err
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rows == 0 {
		return errors.New("user not found")
	}

	return nil
}

// Count gets total number of active users
func (r *UserRepository) Count() (int, error) {
	var count int
	query := "SELECT COUNT(*) FROM users WHERE is_active = true"

	err := r.db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}

	return count, nil
}

// ExistsByUsername checks if username exists
func (r *UserRepository) ExistsByUsername(username string) (bool, error) {
	var exists bool
	query := "SELECT EXISTS(SELECT 1 FROM users WHERE username = $1)"

	err := r.db.QueryRow(query, username).Scan(&exists)
	if err != nil {
		return false, err
	}

	return exists, nil
}

// ExistsByEmail checks if email exists
func (r *UserRepository) ExistsByEmail(email string) (bool, error) {
	var exists bool
	query := "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)"

	err := r.db.QueryRow(query, email).Scan(&exists)
	if err != nil {
		return false, err
	}

	return exists, nil
}

func hashToken(token string) string {
	sum := sha256.Sum256([]byte(token))
	return hex.EncodeToString(sum[:])
}

func (r *UserRepository) StoreRefreshToken(userID int, refreshToken string, expiresAt time.Time) error {
	if r.db == nil {
		return errors.New("database not configured")
	}

	query := `
		INSERT INTO refresh_tokens (user_id, token_hash, expires_at, revoked, created_at)
		VALUES ($1, $2, $3, false, NOW())
	`

	_, err := r.db.Exec(query, userID, hashToken(refreshToken), expiresAt)
	return err
}

func (r *UserRepository) ValidateRefreshToken(refreshToken string) (int, error) {
	if r.db == nil {
		return 0, errors.New("database not configured")
	}

	var userID int
	query := `
		SELECT user_id
		FROM refresh_tokens
		WHERE token_hash = $1
		  AND revoked = false
		  AND expires_at > NOW()
		LIMIT 1
	`

	err := r.db.QueryRow(query, hashToken(refreshToken)).Scan(&userID)
	if err != nil {
		if err == sql.ErrNoRows {
			return 0, errors.New("refresh token not found")
		}
		return 0, err
	}

	return userID, nil
}

func (r *UserRepository) RevokeRefreshToken(refreshToken string) error {
	if r.db == nil {
		return errors.New("database not configured")
	}

	query := `
		UPDATE refresh_tokens
		SET revoked = true
		WHERE token_hash = $1
	`

	_, err := r.db.Exec(query, hashToken(refreshToken))
	return err
}
