# Docker Setup Guide

This guide explains how to run the TripMate backend using Docker.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

1. **Create environment file**

   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your configuration**
   - Update `SECRET_KEY` with a secure random string
   - Configure email settings (MAIL_USERNAME, MAIL_PASSWORD, etc.)
   - Adjust other settings as needed

3. **Start all services**

   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database on port 5432
   - Redis cache on port 6379
   - FastAPI backend on port 8000

4. **Check service status**

   ```bash
   docker-compose ps
   ```

5. **View logs**

   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f backend
   ```

## API Access

Once running, the API will be available at:

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Database Management

### Run Migrations

Migrations run automatically when the backend container starts. To run them manually:

```bash
docker-compose exec backend alembic upgrade head
```

### Create a New Migration

```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Access PostgreSQL Database

```bash
docker-compose exec db psql -U tripmate -d tripmate_db
```

### Populate Database with Sample Data

```bash
docker-compose exec backend python populate_db.py
```

## Development Workflow

### Hot Reload

The backend service is configured with `--reload` flag, so code changes will automatically reload the server.

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes (⚠️ This deletes all data)

```bash
docker-compose down -v
```

### Rebuild Images

If you modify `requirements.txt` or `Dockerfile`:

```bash
docker-compose up -d --build
```

### Run Commands Inside Container

```bash
# Access backend container shell
docker-compose exec backend bash

# Run Python commands
docker-compose exec backend python -c "print('Hello')"
```

## Troubleshooting

### Backend can't connect to database

1. Check if all services are running:

   ```bash
   docker-compose ps
   ```

2. Check database logs:

   ```bash
   docker-compose logs db
   ```

3. Wait for database to be ready (it might take a few seconds on first start)

### Port already in use

If ports 8000, 5432, or 6379 are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8080:8000" # Change host port (left side) as needed
```

### View detailed logs

```bash
docker-compose logs --tail=100 -f backend
```

### Reset everything

```bash
docker-compose down -v
docker-compose up -d --build
```

## Production Deployment

For production:

1. **Update `.env` file**:
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure proper email credentials
   - Set appropriate `FRONTEND_URL_RESET`

2. **Modify docker-compose.yml**:
   - Remove volume mounts for hot-reload
   - Remove `--reload` flag from command
   - Use proper secrets management
   - Configure reverse proxy (nginx, traefik)
   - Set up SSL/TLS certificates

3. **Security**:
   - Never commit `.env` file to version control
   - Use Docker secrets or environment variable injection
   - Restrict database access
   - Enable firewall rules

## Services Overview

| Service | Container Name   | Port | Description            |
| ------- | ---------------- | ---- | ---------------------- |
| backend | tripmate_backend | 8000 | FastAPI application    |
| db      | tripmate_db      | 5432 | PostgreSQL 15 database |
| redis   | tripmate_redis   | 6379 | Redis cache            |

## Useful Commands

```bash
# Restart a specific service
docker-compose restart backend

# View resource usage
docker stats

# Clean up unused Docker resources
docker system prune -a

# Export database
docker-compose exec db pg_dump -U tripmate tripmate_db > backup.sql

# Import database
cat backup.sql | docker-compose exec -T db psql -U tripmate tripmate_db
```
