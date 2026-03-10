from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_PORT: int = 5432
    DB_HOST: str = "localhost"
    DB_NAME: str = "dev_db"
    DB_USER: str = "dev"
    DB_PASSWORD: str = "dev"
    APPLICATION_NAME: str = "TripMate"
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = False
    FRONTEND_URL_RESET: str = "http://localhost:5173"
    GOOGLE_CLIENT_ID: str = ""
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    GEMINI_API_KEY: str = ""

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def DATABASE_URL(self) -> str:
        # SQLite (for local development)
        return "sqlite+aiosqlite:///./volumes/sqlite_data/tripmate.db"

        # PostgreSQL (for Docker and production - uncomment if needed)
        # return (
        #     f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
        #     f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        # )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        # SQLite (for Alembic migrations)
        return "sqlite:///./volumes/sqlite_data/tripmate.db"

        # PostgreSQL (for Alembic migrations - uncomment if needed)
        # return (
        #     f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
        #     f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        # )

    class Config:
        env_file = ".env"


config = Settings()
