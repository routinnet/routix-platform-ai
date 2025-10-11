from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.orm import relationship

from src.core.database import Base


class Algorithm(Base):
    __tablename__ = "algorithms"

    id = Column(String, primary_key=True)  # e.g., "basic", "premium", "pro"
    name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    cost_credits = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    parameters = Column(Text, nullable=True)  # JSON string with algorithm-specific parameters
    
    # Relationships
    generations = relationship("Generation", back_populates="algorithm")

    def __repr__(self):
        return f"<Algorithm(id={self.id}, name={self.name}, cost={self.cost_credits})>"

    @property
    def is_available(self) -> bool:
        """Check if algorithm is available for use."""
        return self.is_active

    @classmethod
    def get_default_algorithms(cls):
        """Get default algorithm configurations."""
        return [
            {
                "id": "basic",
                "name": "basic",
                "display_name": "Basic Generation",
                "description": "Fast and cost-effective thumbnail generation using Stable Diffusion",
                "cost_credits": 1,
                "is_active": True,
                "parameters": {
                    "model": "stable-diffusion",
                    "quality": "standard",
                    "speed": "fast",
                    "resolution": "1280x720"
                }
            },
            {
                "id": "premium",
                "name": "premium",
                "display_name": "Premium Generation", 
                "description": "High-quality thumbnail generation with advanced AI models",
                "cost_credits": 3,
                "is_active": True,
                "parameters": {
                    "model": "dall-e-3",
                    "quality": "high",
                    "speed": "medium",
                    "resolution": "1280x720"
                }
            },
            {
                "id": "pro",
                "name": "pro",
                "display_name": "Pro Generation",
                "description": "Professional-grade thumbnails with Midjourney quality",
                "cost_credits": 5,
                "is_active": True,
                "parameters": {
                    "model": "midjourney",
                    "quality": "ultra",
                    "speed": "slow",
                    "resolution": "1280x720"
                }
            }
        ]
