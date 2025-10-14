from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import os
import secrets


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./routix.db"
    
    # Security
    secret_key: str = Field(
        default=None,
        description="Secret key for JWT tokens - MUST be set in production"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @validator('secret_key', pre=True, always=True)
    def validate_secret_key(cls, v, values):
        """Validate and auto-generate secret key if needed"""
        environment = os.getenv('ENVIRONMENT', 'development')
        
        # اگر secret_key تنظیم نشده
        if v is None or v == "your-secret-key-change-in-production":
            if environment == 'production':
                raise ValueError(
                    "❌ CRITICAL: SECRET_KEY must be set in production!\n"
                    "Generate one using: python -c 'import secrets; print(secrets.token_urlsafe(32))'\n"
                    "Then set it in environment: export SECRET_KEY='your-generated-key'"
                )
            else:
                # در development، یک کلید موقت تولید کن
                generated_key = secrets.token_urlsafe(32)
                print(f"⚠️  WARNING: Using auto-generated SECRET_KEY for development")
                print(f"🔑 Generated key: {generated_key}")
                print(f"💡 TIP: Set SECRET_KEY in .env file for persistence")
                return generated_key
        
        # بررسی طول کلید
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long!")
        
        return v
    
    # AI APIs
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    midjourney_api_key: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    upload_dir: str = "uploads"
    
    # Credits
    default_credits: int = 10
    
    # Generation
    max_generations_per_hour: int = 20
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Application
    debug: bool = True
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
