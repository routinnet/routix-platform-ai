from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.core.database import Base


class GenerationStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Generation(Base):
    __tablename__ = "generations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    algorithm_id = Column(String, ForeignKey("algorithms.id"), nullable=False)
    
    # Generation details
    prompt = Column(Text, nullable=False)
    reference_images = Column(Text, nullable=True)  # JSON array of image URLs
    parameters = Column(Text, nullable=True)  # JSON object with generation parameters
    
    # Status and progress
    status = Column(Enum(GenerationStatus), default=GenerationStatus.QUEUED)
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    
    # Results
    result_url = Column(String, nullable=True)
    result_metadata = Column(Text, nullable=True)  # JSON with additional result data
    
    # Credits and billing
    credits_used = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="generations")
    conversation = relationship("Conversation", back_populates="generations")
    algorithm = relationship("Algorithm", back_populates="generations")

    def __repr__(self):
        return f"<Generation(id={self.id}, status={self.status}, user_id={self.user_id})>"

    @property
    def is_completed(self) -> bool:
        """Check if generation is completed."""
        return self.status == GenerationStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if generation failed."""
        return self.status == GenerationStatus.FAILED

    @property
    def is_processing(self) -> bool:
        """Check if generation is currently processing."""
        return self.status == GenerationStatus.PROCESSING

    @property
    def duration_seconds(self) -> int:
        """Get generation duration in seconds."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return 0

    def mark_as_started(self):
        """Mark generation as started."""
        self.status = GenerationStatus.PROCESSING
        self.started_at = datetime.utcnow()

    def mark_as_completed(self, result_url: str, metadata: str = None):
        """Mark generation as completed."""
        self.status = GenerationStatus.COMPLETED
        self.progress = 100
        self.result_url = result_url
        self.result_metadata = metadata
        self.completed_at = datetime.utcnow()

    def mark_as_failed(self, error_message: str):
        """Mark generation as failed."""
        self.status = GenerationStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()

    def update_progress(self, progress: int):
        """Update generation progress."""
        self.progress = max(0, min(100, progress))


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String(20), nullable=False)  # "purchase", "usage", "refund", "bonus"
    amount = Column(Integer, nullable=False)  # Positive for additions, negative for deductions
    description = Column(String(255), nullable=False)
    reference_id = Column(String, nullable=True)  # Reference to generation, purchase, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="credit_transactions")

    def __repr__(self):
        return f"<CreditTransaction(id={self.id}, type={self.type}, amount={self.amount})>"
