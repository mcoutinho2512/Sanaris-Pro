from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Sanaris Pro"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8888
    
    # Database
    DATABASE_URL: str = "postgresql://sanaris_user:sanaris_password@localhost:5433/sanaris_db"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT (mantendo compatibilidade com nomes antigos e novos)
    SECRET_KEY: str = "sua_chave_super_secreta_aqui_mude_em_producao_123456789"
    JWT_SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    JWT_ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3001", "http://localhost:3000"]
    CORS_ORIGINS: Optional[str] = None
    
    # Upload
    MAX_UPLOAD_SIZE: int = 10485760
    UPLOAD_DIR: str = "/home/administrador/sanaris-pro/sanaris/uploads"
    
    # Logs
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/home/administrador/sanaris-pro/sanaris/logs/backend/sanaris.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permitir campos extras

settings = Settings()
