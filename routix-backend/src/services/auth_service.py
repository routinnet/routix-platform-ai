from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from src.models.user import User
from src.core.security import verify_password, get_password_hash
from src.schemas.user import UserCreate, UserLogin


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
        """Create a new user."""
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[User]:
        """Authenticate user with email and password."""
        
        # Get user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user
    
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
        """Get user by email."""
        
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(username: str, db: AsyncSession) -> Optional[User]:
        """Get user by username."""
        
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(user_id: str, db: AsyncSession) -> Optional[User]:
        """Get user by ID."""
        
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user_password(user: User, new_password: str, db: AsyncSession) -> User:
        """Update user password."""
        
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def deactivate_user(user: User, db: AsyncSession) -> User:
        """Deactivate user account."""
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def activate_user(user: User, db: AsyncSession) -> User:
        """Activate user account."""
        
        user.is_active = True
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return user
