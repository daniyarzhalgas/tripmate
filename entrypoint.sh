#!/bin/bash
set -e

# PostgreSQL readiness check (Commented out - using SQLite)
# echo "Waiting for PostgreSQL to be ready..."
# until pg_isready -h "$DB_HOST" -U "$DB_USER"; do
#   echo "PostgreSQL is unavailable - sleeping"
#   sleep 1
# done
# echo "PostgreSQL is up - executing command"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Execute the main command (passed as arguments)
exec "$@"
