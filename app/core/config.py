from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APPLICATION_NAME: str = "TripMate"
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = False
    FRONTEND_URL_RESET: str = "http://localhost:5173"

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "dev_db"
    DB_USER: str = "dev"
    DB_PASSWORD: str = "dev"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Email
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_TIMEOUT_SECONDS: int = 60 * 5
    PLAN_SERVICE_URL: str = "http://localhost:8001/generate"

    # Unsplash API
    UNSPLASH_ACCESS_KEY: str = ""
    UNSPLASH_SECRET_KEY: str = ""

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def DATABASE_URL(self) -> str:
        # SQLite for local development; switch to PostgreSQL for production
        return "sqlite+aiosqlite:///./tripmate.db"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        # SQLite for Alembic migrations; switch to PostgreSQL for production
        return "sqlite:///./tripmate.db"

    model_config = SettingsConfigDict(env_file=".env")


config = Settings()
