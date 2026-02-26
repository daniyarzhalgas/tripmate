# TripMate

A travel companion matching platform built with FastAPI.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:
   Create a `.env` file based on your configuration needs.

3. Run database migrations:

```bash
alembic upgrade head
```

4. Populate initial data (languages, interests, travel styles):

```bash
python populate_db.py
```

5. Start the application:

```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Information

The application uses SQLite by default. The database file `tripmate.db` will be created in the project root.

To switch to PostgreSQL, uncomment the PostgreSQL configuration in `app/core/config.py`.
