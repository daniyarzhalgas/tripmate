from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_PORT: int = 5432
    DB_HOST: str = "localhost"
    DB_NAME: str = "dev_db"
    DB_USER: str = "dev"
    DB_PASSWORD: str = "dev"

    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    EMAIL_ENABLED: bool = False
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 25
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "no-reply@tripmate.local"
    SMTP_USE_TLS: bool = False

    FRONTEND_RESET_PASSWORD_URL: str | None = None

    class Config:
        env_file = ".env"


config = Settings()
