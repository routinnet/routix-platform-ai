"""
Base model module with smart UUID handling for both PostgreSQL and SQLite
"""
import os
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# تشخیص نوع دیتابیس
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./routix.db")
IS_SQLITE = "sqlite" in DATABASE_URL.lower()


def get_uuid_column():
    """
    برگرداندن نوع UUID مناسب بر اساس دیتابیس
    
    - PostgreSQL: استفاده از UUID بومی برای بهره‌وری بهتر
    - SQLite: استفاده از String برای سازگاری
    
    Returns:
        Column: ستون UUID با تنظیمات مناسب
    """
    if IS_SQLITE:
        return Column(
            String(36),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
            nullable=False
        )
    else:
        return Column(
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )


class BaseModel(Base):
    """
    Base model with automatic timestamp management
    
    All models should inherit from this to get:
    - Automatic created_at timestamp
    - Automatic updated_at timestamp
    - Smart UUID handling
    """
    __abstract__ = True
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def uuid_to_str(uuid_value) -> str:
    """
    تبدیل UUID به string برای سازگاری با SQLite
    
    Args:
        uuid_value: مقدار UUID (می‌تواند str یا UUID باشد)
        
    Returns:
        str: نسخه string از UUID
    """
    if isinstance(uuid_value, str):
        return uuid_value
    elif isinstance(uuid_value, uuid.UUID):
        return str(uuid_value)
    else:
        return str(uuid_value)


def str_to_uuid(str_value: str):
    """
    تبدیل string به UUID برای PostgreSQL
    
    Args:
        str_value: مقدار string
        
    Returns:
        UUID object برای PostgreSQL یا string برای SQLite
    """
    if IS_SQLITE:
        return str_value
    else:
        return uuid.UUID(str_value) if isinstance(str_value, str) else str_value


# Helper function برای migration
def generate_uuid() -> str:
    """Generate a new UUID string"""
    return str(uuid.uuid4())


# Export useful functions
__all__ = [
    'Base',
    'BaseModel',
    'get_uuid_column',
    'uuid_to_str',
    'str_to_uuid',
    'generate_uuid',
    'IS_SQLITE'
]
