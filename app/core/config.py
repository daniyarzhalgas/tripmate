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

    GOOGLE_CLIENT_ID: str  
    MAIL_USERNAME: str 
    MAIL_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


config = Settings()
