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


@router.post("/credits/purchase/intent")
async def create_payment_intent(
    package_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a payment intent for credit purchase."""
    from src.services.payment_service import PaymentService
    
    payment_service = PaymentService()
    
    try:
        payment_intent = await payment_service.create_payment_intent(
            user=current_user,
            package_id=package_id,
            db=db
        )
        
        return payment_intent
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )


@router.post("/credits/purchase")
async def purchase_credits(
    package_id: str,
    payment_method_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process credit purchase with payment.
    
    This endpoint processes the actual payment and adds credits to the user account.
    """
    from src.services.payment_service import PaymentService
    
    payment_service = PaymentService()
    
    try:
        result = await payment_service.process_payment(
            user=current_user,
            package_id=package_id,
            payment_method_id=payment_method_id,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Payment failed")
            )
        
        return {
            "success": True,
            "message": f"Successfully purchased {result['credits_added']} credits",
            "transaction_id": result["transaction_id"],
            "credits_added": result["credits_added"],
            "new_balance": result["new_balance"],
            "package": result["package"]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Payment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment processing failed"
        )


@router.get("/credits/packages")
async def get_credit_packages():
    """Get available credit packages."""
    from src.services.payment_service import PaymentService
    
    payment_service = PaymentService()
    packages = payment_service.get_packages()
    
    return {"packages": list(packages.values())}


@router.post("/credits/webhook")
async def payment_webhook(
    event_type: str,
    event_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle payment gateway webhooks.
    
    This endpoint receives and processes webhook events from the payment gateway.
    In production, this should verify webhook signatures for security.
    """
    from src.services.payment_service import PaymentService
    
    payment_service = PaymentService()
    
    try:
        result = await payment_service.handle_webhook(
            event_type=event_type,
            event_data=event_data,
            db=db
        )
        
        return result
        
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


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
