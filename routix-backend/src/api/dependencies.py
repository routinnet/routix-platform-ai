from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.core.database import get_db
from src.core.security import verify_token
from src.models.user import User
from src.models.algorithm import Algorithm

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def verify_algorithm_exists(
    algorithm_id: str,
    db: AsyncSession = Depends(get_db)
) -> Algorithm:
    """Verify that an algorithm exists and is active."""
    result = await db.execute(select(Algorithm).where(Algorithm.id == algorithm_id))
    algorithm = result.scalar_one_or_none()
    
    if not algorithm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Algorithm '{algorithm_id}' not found"
        )
    
    if not algorithm.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Algorithm '{algorithm_id}' is not available"
        )
    
    return algorithm


async def verify_user_credits(
    user: User,
    required_credits: int
) -> bool:
    """Verify that user has enough credits."""
    if user.credits < required_credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {required_credits}, Available: {user.credits}"
        )
    return True


class Pagination:
    """Pagination helper."""
    
    def __init__(self, page: int = 1, per_page: int = 20):
        self.page = max(1, page)
        self.per_page = min(100, max(1, per_page))  # Max 100 items per page
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        return self.per_page
    
    def get_pagination_info(self, total: int) -> dict:
        """Get pagination information."""
        total_pages = (total + self.per_page - 1) // self.per_page
        
        return {
            "total": total,
            "page": self.page,
            "per_page": self.per_page,
            "total_pages": total_pages,
            "has_next": self.page < total_pages,
            "has_prev": self.page > 1
        }


def get_pagination(page: int = 1, per_page: int = 20) -> Pagination:
    """Dependency to get pagination parameters."""
    return Pagination(page, per_page)
