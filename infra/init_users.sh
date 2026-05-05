#!/bin/bash
# Initialize Users Table and Create Default Users
# Run this script after migrations are applied

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 AgroVision Users Initialization${NC}"
echo -e "${BLUE}========================================${NC}"

# Database credentials
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-agrovision}"
DB_NAME="${DB_NAME:-agrovision}"
DB_PASSWORD="${DB_PASSWORD:-agrovision}"

export PGPASSWORD=$DB_PASSWORD

echo ""
echo -e "${YELLOW}📋 Database Configuration:${NC}"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "User: $DB_USER"
echo "Database: $DB_NAME"
echo ""

# Check if PostgreSQL is accessible
echo -e "${YELLOW}🔍 Checking PostgreSQL connection...${NC}"
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to PostgreSQL${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Connected to PostgreSQL${NC}"

# Check if users table exists
echo -e "${YELLOW}🔍 Checking if users table exists...${NC}"
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1 FROM information_schema.tables WHERE table_name='users'" | grep -q 1; then
    echo -e "${GREEN}✅ Users table already exists${NC}"
else
    echo -e "${YELLOW}⚠️ Users table does not exist. Run migrations first:${NC}"
    echo "   cd infra/alembic && alembic upgrade head"
    exit 1
fi

# Check if admin user exists
echo -e "${YELLOW}🔍 Checking if admin user exists...${NC}"
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1 FROM users WHERE username='admin'" | grep -q 1; then
    echo -e "${GREEN}✅ Admin user already exists${NC}"
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}👤 Current Users:${NC}"
    echo -e "${BLUE}========================================${NC}"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT id, username, email, role, is_active, created_at FROM users ORDER BY id;"
    exit 0
fi

# Create users using SQL
echo -e "${YELLOW}📝 Creating default users...${NC}"
echo ""

# Create admin user (password: password123)
# Bcrypt hash generated in Go: utils.HashPassword("password123")
ADMIN_HASH='$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcg7b3XeKeUxWdeS86E36gZvWFm'

# Create operator user (password: operator123)
OPERATOR_HASH='$2a$10$0RtMiWLKgfKDp9YkTvfN2eKD.RuBf4QH5G8KQMV2P8nF.6zw9pN6a'

# Create viewer user (password: viewer123)
VIEWER_HASH='$2a$10$0RtMiWLKgfKDp9YkTvfN2eKD.RuBf4QH5G8KQMV2P8nF.6zw9pN6a'

psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" << EOF
-- Insert admin user
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES ('admin', 'admin@agrovision.local', '\$2a\$10\$N9qo8uLOickgx2ZMRZoMyeIjZAgcg7b3XeKeUxWdeS86E36gZvWFm', 'Administrator', 'admin', true)
ON CONFLICT (username) DO NOTHING;

-- Insert operator user
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES ('operator', 'operator@agrovision.local', '\$2a\$10\$0RtMiWLKgfKDp9YkTvfN2eKD.RuBf4QH5G8KQMV2P8nF.6zw9pN6a', 'Operador', 'operator', true)
ON CONFLICT (username) DO NOTHING;

-- Insert viewer user
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES ('viewer', 'viewer@agrovision.local', '\$2a\$10\$0RtMiWLKgfKDp9YkTvfN2eKD.RuBf4QH5G8KQMV2P8nF.6zw9pN6a', 'Visualizador', 'viewer', true)
ON CONFLICT (username) DO NOTHING;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Default users created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create default users${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}👤 Users Created:${NC}"
echo -e "${BLUE}========================================${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT id, username, email, role, is_active, created_at FROM users ORDER BY id;"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Users initialization completed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}📋 Default Credentials:${NC}"
echo "  • Username: admin"
echo "  • Password: password123"
echo ""
echo "  • Username: operator"
echo "  • Password: operator123"
echo ""
echo "  • Username: viewer"
echo "  • Password: viewer123"
echo ""
