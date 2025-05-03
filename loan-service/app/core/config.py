import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Loan Service"
    API_PREFIX: str = "/api/loans"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/loan_db")
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://user-service:8081")
    BOOK_SERVICE_URL: str = os.getenv("BOOK_SERVICE_URL", "http://book-service:8082")
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
