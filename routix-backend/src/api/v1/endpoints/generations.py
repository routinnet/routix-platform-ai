from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List
from uuid import UUID
import json

from src.core.database import get_db
from src.models.user import User
from src.models.generation import Generation, GenerationStatus, CreditTransaction
from src.models.algorithm import Algorithm
from src.schemas.generation import (
    GenerationCreate,
    GenerationResponse,
    GenerationList,
    AlgorithmResponse,
    GenerationProgress,
    GenerationStats,
    CreditTransactionResponse,
    CreditTransactionList
)
from src.api.dependencies import (
    get_current_active_user,
    get_pagination,
    Pagination,
    verify_algorithm_exists,
    verify_user_credits
)
from src.services.generation_service import GenerationService

router = APIRouter()


@router.get("/algorithms", response_model=List[AlgorithmResponse])
async def get_algorithms(
    db: AsyncSession = Depends(get_db)
):
    """Get available generation algorithms."""
    
    result = await db.execute(
        select(Algorithm).where(Algorithm.is_active == True)
    )
    algorithms = result.scalars().all()
    
    return [AlgorithmResponse.model_validate(algo) for algo in algorithms]


@router.post("/generations", response_model=GenerationResponse)
async def create_generation(
    generation_data: GenerationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new thumbnail generation."""
    
    # Verify algorithm exists and is active
    algorithm = await verify_algorithm_exists(generation_data.algorithm_id, db)
    
    # Verify user has enough credits
    await verify_user_credits(current_user, algorithm.cost_credits)
    
    # Create generation record
    generation = Generation(
        user_id=current_user.id,
        conversation_id=generation_data.conversation_id,
        algorithm_id=generation_data.algorithm_id,
        prompt=generation_data.prompt,
        reference_images=json.dumps(generation_data.reference_images) if generation_data.reference_images else None,
        parameters=json.dumps(generation_data.parameters) if generation_data.parameters else None,
        credits_used=algorithm.cost_credits,
        status=GenerationStatus.QUEUED
    )
    
    db.add(generation)
    
    # Deduct credits from user
    current_user.deduct_credits(algorithm.cost_credits)
    
    # Create credit transaction
    transaction = CreditTransaction(
        user_id=current_user.id,
        type="usage",
        amount=-algorithm.cost_credits,
        description=f"Thumbnail generation using {algorithm.display_name}",
        reference_id=generation.id
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(generation)
    
    # Start generation in background
    generation_service = GenerationService()
    background_tasks.add_task(
        generation_service.process_generation,
        generation.id,
        db
    )
    
    return GenerationResponse.model_validate(generation)


@router.get("/generations", response_model=GenerationList)
async def get_generations(
    pagination: Pagination = Depends(get_pagination),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's generations with pagination."""
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Generation.id)).where(Generation.user_id == current_user.id)
    )
    total = count_result.scalar()
    
    # Get generations
    result = await db.execute(
        select(Generation)
        .where(Generation.user_id == current_user.id)
        .order_by(desc(Generation.created_at))
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    generations = result.scalars().all()
    
    # Convert to response format
    generation_responses = []
    for gen in generations:
        gen_data = GenerationResponse.model_validate(gen)
        gen_data.duration_seconds = gen.duration_seconds
        generation_responses.append(gen_data)
    
    pagination_info = pagination.get_pagination_info(total)
    
    return GenerationList(
        generations=generation_responses,
        **pagination_info
    )


@router.get("/generations/{generation_id}", response_model=GenerationResponse)
async def get_generation(
    generation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific generation."""
    
    result = await db.execute(
        select(Generation).where(
            Generation.id == generation_id,
            Generation.user_id == current_user.id
        )
    )
    generation = result.scalar_one_or_none()
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    
    gen_data = GenerationResponse.model_validate(generation)
    gen_data.duration_seconds = generation.duration_seconds
    
    return gen_data


@router.get("/generations/{generation_id}/status", response_model=GenerationProgress)
async def get_generation_status(
    generation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get generation status and progress."""
    
    result = await db.execute(
        select(Generation).where(
            Generation.id == generation_id,
            Generation.user_id == current_user.id
        )
    )
    generation = result.scalar_one_or_none()
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    
    return GenerationProgress(
        generation_id=generation.id,
        status=generation.status,
        progress=generation.progress,
        message=generation.error_message if generation.is_failed else None
    )


@router.delete("/generations/{generation_id}")
async def cancel_generation(
    generation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a generation (only if queued or processing)."""
    
    result = await db.execute(
        select(Generation).where(
            Generation.id == generation_id,
            Generation.user_id == current_user.id
        )
    )
    generation = result.scalar_one_or_none()
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    
    if generation.status in [GenerationStatus.COMPLETED, GenerationStatus.FAILED, GenerationStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed, failed, or already cancelled generation"
        )
    
    # Cancel generation
    generation.status = GenerationStatus.CANCELLED
    await db.commit()
    
    return {"message": "Generation cancelled successfully"}


@router.get("/stats", response_model=GenerationStats)
async def get_generation_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's generation statistics."""
    
    # Total generations
    total_result = await db.execute(
        select(func.count(Generation.id)).where(Generation.user_id == current_user.id)
    )
    total_generations = total_result.scalar()
    
    # Successful generations
    success_result = await db.execute(
        select(func.count(Generation.id)).where(
            Generation.user_id == current_user.id,
            Generation.status == GenerationStatus.COMPLETED
        )
    )
    successful_generations = success_result.scalar()
    
    # Failed generations
    failed_result = await db.execute(
        select(func.count(Generation.id)).where(
            Generation.user_id == current_user.id,
            Generation.status == GenerationStatus.FAILED
        )
    )
    failed_generations = failed_result.scalar()
    
    # Total credits used
    credits_result = await db.execute(
        select(func.sum(Generation.credits_used)).where(Generation.user_id == current_user.id)
    )
    total_credits_used = credits_result.scalar() or 0
    
    # Most used algorithm
    algo_result = await db.execute(
        select(Generation.algorithm_id, func.count(Generation.id).label('count'))
        .where(Generation.user_id == current_user.id)
        .group_by(Generation.algorithm_id)
        .order_by(desc('count'))
        .limit(1)
    )
    most_used_algo = algo_result.first()
    most_used_algorithm = most_used_algo[0] if most_used_algo else None
    
    return GenerationStats(
        total_generations=total_generations,
        successful_generations=successful_generations,
        failed_generations=failed_generations,
        total_credits_used=total_credits_used,
        most_used_algorithm=most_used_algorithm
    )


@router.get("/credits/transactions", response_model=CreditTransactionList)
async def get_credit_transactions(
    pagination: Pagination = Depends(get_pagination),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's credit transaction history."""
    
    # Get total count
    count_result = await db.execute(
        select(func.count(CreditTransaction.id)).where(CreditTransaction.user_id == current_user.id)
    )
    total = count_result.scalar()
    
    # Get transactions
    result = await db.execute(
        select(CreditTransaction)
        .where(CreditTransaction.user_id == current_user.id)
        .order_by(desc(CreditTransaction.created_at))
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    transactions = result.scalars().all()
    
    pagination_info = pagination.get_pagination_info(total)
    
    return CreditTransactionList(
        transactions=[CreditTransactionResponse.model_validate(tx) for tx in transactions],
        **pagination_info
    )
