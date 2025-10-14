from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageBase(BaseModel):
    role: str = Field(..., pattern=r"^(user|assistant)$")
    content: str = Field(..., min_length=1)
    attachments: Optional[str] = None
    metadata: Optional[str] = None


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    first_message: Optional[str] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    is_archived: Optional[bool] = None


class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationDetail(ConversationResponse):
    messages: List[MessageResponse] = []


class ConversationList(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    attachments: Optional[List[str]] = None
    metadata: Optional[dict] = None


class ChatResponse(BaseModel):
    message: MessageResponse
    conversation_id: str
    requires_generation: bool = False
    generation_id: Optional[str] = None
