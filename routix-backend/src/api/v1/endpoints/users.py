from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.core.database import get_db
from src.models.user import User
from src.models.generation import Generation, GenerationStatus, CreditTransaction
from src.schemas.user import UserResponse, UserProfile
from src.api.dependencies import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's detailed profile with statistics."""
    
    # Get generation statistics
    total_generations_result = await db.execute(
        select(func.count(Generation.id)).where(Generation.user_id == current_user.id)
    )
    total_generations = total_generations_result.scalar()
    
    successful_generations_result = await db.execute(
        select(func.count(Generation.id)).where(
            Generation.user_id == current_user.id,
            Generation.status == GenerationStatus.COMPLETED
        )
    )
    successful_generations = successful_generations_result.scalar()
    
    # Get total credits used
    credits_used_result = await db.execute(
        select(func.sum(CreditTransaction.amount)).where(
            CreditTransaction.user_id == current_user.id,
            CreditTransaction.type == "usage"
        )
    )
    total_credits_used = abs(credits_used_result.scalar() or 0)
    
    # Create profile response
    profile = UserProfile.model_validate(current_user)
    profile.total_generations = total_generations
    profile.successful_generations = successful_generations
    profile.total_credits_used = total_credits_used
    
    return profile


@router.get("/credits")
async def get_user_credits(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's credit balance."""
    
    return {
        "credits": current_user.credits,
        "subscription_tier": current_user.subscription_tier
    }


@router.post("/credits/purchase")
async def purchase_credits(
    amount: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Purchase credits (placeholder for payment integration)."""
    
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    # TODO: Integrate with payment processor
    # For now, just add credits (this would be called after successful payment)
    
    current_user.add_credits(amount)
    
    # Create transaction record
    transaction = CreditTransaction(
        user_id=current_user.id,
        type="purchase",
        amount=amount,
        description=f"Purchased {amount} credits"
    )
    
    db.add(transaction)
    await db.commit()
    
    return {
        "message": f"Successfully purchased {amount} credits",
        "new_balance": current_user.credits
    }


@router.get("/usage-stats")
async def get_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed usage statistics for the current user."""
    
    # Generations by status
    status_stats = {}
    for status in GenerationStatus:
        result = await db.execute(
            select(func.count(Generation.id)).where(
                Generation.user_id == current_user.id,
                Generation.status == status
            )
        )
        status_stats[status.value] = result.scalar()
    
    # Credits by transaction type
    credit_stats = {}
    for tx_type in ["purchase", "usage", "refund", "bonus"]:
        result = await db.execute(
            select(func.sum(CreditTransaction.amount)).where(
                CreditTransaction.user_id == current_user.id,
                CreditTransaction.type == tx_type
            )
        )
        credit_stats[tx_type] = result.scalar() or 0
    
    # Recent activity (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_generations_result = await db.execute(
        select(func.count(Generation.id)).where(
            Generation.user_id == current_user.id,
            Generation.created_at >= thirty_days_ago
        )
    )
    recent_generations = recent_generations_result.scalar()
    
    return {
        "generations_by_status": status_stats,
        "credits_by_type": credit_stats,
        "recent_activity": {
            "generations_last_30_days": recent_generations
        },
        "account_info": {
            "current_credits": current_user.credits,
            "subscription_tier": current_user.subscription_tier,
            "member_since": current_user.created_at,
            "last_login": current_user.last_login
        }
    }
