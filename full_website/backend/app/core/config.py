# backend/app/core/config.py
# Purpose: Application configuration settings
# Author: Antigravity

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
from typing import Optional

class Settings(BaseSettings):
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    
    BACKEND_SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    WEBHOOK_SECRET: str = "webhooksecret"
    
    FRONTEND_URL: str = "http://localhost:5174"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.POSTGRES_USER and self.POSTGRES_HOST:
             return str(PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            ))
        return "sqlite+aiosqlite:///./test.db"

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore", case_sensitive=True)

settings = Settings()
