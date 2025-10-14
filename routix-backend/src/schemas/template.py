from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TemplateBase(BaseModel):
    """Base template schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=50)
    style: str = Field(..., min_length=1, max_length=50)
    mood: str = Field(..., min_length=1, max_length=50)
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    elements: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_premium: bool = False


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    preview_image: Optional[str] = None
    template_file: Optional[str] = None


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    elements: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Schema for template response."""
    id: str
    usage_count: int
    rating: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateWithMatch(TemplateResponse):
    """Template response with match score."""
    match_score: float = Field(..., ge=0.0, le=1.0)


class TemplateList(BaseModel):
    """Paginated list of templates."""
    templates: List[TemplateResponse]
    total: int
    page: int
    limit: int
    pages: int


class TemplateSearchRequest(BaseModel):
    """Schema for searching templates."""
    category: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[List[str]] = None
    is_premium: Optional[bool] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)


class TemplateMatchRequest(BaseModel):
    """Schema for finding matching templates."""
    prompt: str = Field(..., min_length=1)
    reference_images: Optional[List[str]] = None
    limit: int = Field(5, ge=1, le=20)
    min_match_score: float = Field(0.0, ge=0.0, le=1.0)
