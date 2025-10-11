from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from src.models.generation import GenerationStatus


class GenerationBase(BaseModel):
    prompt: str = Field(..., min_length=1)
    algorithm_id: str
    reference_images: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None


class GenerationCreate(GenerationBase):
    conversation_id: Optional[UUID] = None


class GenerationUpdate(BaseModel):
    status: Optional[GenerationStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None
    result_url: Optional[str] = None
    result_metadata: Optional[Dict[str, Any]] = None


class GenerationResponse(GenerationBase):
    id: UUID
    user_id: UUID
    conversation_id: Optional[UUID] = None
    status: GenerationStatus
    progress: int
    error_message: Optional[str] = None
    result_url: Optional[str] = None
    result_metadata: Optional[Dict[str, Any]] = None
    credits_used: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None

    class Config:
        from_attributes = True


class GenerationList(BaseModel):
    generations: List[GenerationResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class AlgorithmResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    cost_credits: int
    is_active: bool
    parameters: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class GenerationProgress(BaseModel):
    generation_id: UUID
    status: GenerationStatus
    progress: int
    message: Optional[str] = None
    estimated_completion: Optional[datetime] = None


class GenerationStats(BaseModel):
    total_generations: int
    successful_generations: int
    failed_generations: int
    total_credits_used: int
    average_completion_time: Optional[float] = None
    most_used_algorithm: Optional[str] = None


class CreditTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    amount: int
    description: str
    reference_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CreditTransactionList(BaseModel):
    transactions: List[CreditTransactionResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
