from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    PROJECT_NAME: str = "Testica API"
    DATABASE_URL: str  # e.g. postgresql+asyncpg://user:pass@localhost:5432/dbname
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
print(settings.dict())