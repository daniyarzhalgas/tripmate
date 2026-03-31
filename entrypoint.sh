#!/bin/bash
set -e

# Create uploads directory if it doesn't exist
echo "Creating uploads directory..."
mkdir -p /app/uploads

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until python -c "import psycopg2; psycopg2.connect(host='$DB_HOST', port='$DB_PORT', user='$DB_USER', password='$DB_PASSWORD', dbname='$DB_NAME')" 2>/dev/null; do
  echo "PostgreSQL is unavailable - retrying in 2s..."
  sleep 2
done
echo "PostgreSQL is ready."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Populate database with initial data
echo "Populating database with initial data..."
python populate_db.py

# Execute the main command (passed as arguments)
exec "$@"
