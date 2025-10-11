from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import List
import json

from src.core.database import get_db
from src.models.user import User
from src.models.conversation import Conversation, Message
from src.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetail,
    ConversationList,
    MessageCreate,
    MessageResponse,
    ChatRequest,
    ChatResponse
)
from src.api.dependencies import get_current_active_user, get_pagination, Pagination

router = APIRouter()


@router.get("/conversations", response_model=ConversationList)
async def get_conversations(
    pagination: Pagination = Depends(get_pagination),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's conversations with pagination."""
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.user_id == current_user.id,
            Conversation.is_archived == False
        )
    )
    total = count_result.scalar()
    
    # Get conversations
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.user_id == current_user.id,
            Conversation.is_archived == False
        )
        .order_by(desc(Conversation.updated_at))
        .offset(pagination.offset)
        .limit(pagination.limit)
        .options(selectinload(Conversation.messages))
    )
    conversations = result.scalars().all()
    
    # Convert to response format
    conversation_responses = []
    for conv in conversations:
        conv_dict = {
            "id": conv.id,
            "user_id": conv.user_id,
            "title": conv.title,
            "is_archived": conv.is_archived,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": conv.get_message_count(),
            "last_message_at": conv.get_last_message_at()
        }
        conv_data = ConversationResponse.model_validate(conv_dict)
        conversation_responses.append(conv_data)
    
    pagination_info = pagination.get_pagination_info(total)
    
    return ConversationList(
        conversations=conversation_responses,
        **pagination_info
    )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation."""
    
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title or "New Conversation"
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    # Add first message if provided
    if conversation_data.first_message:
        message = Message(
            conversation_id=conversation.id,
            role="user",
            content=conversation_data.first_message
        )
        db.add(message)
        
        # Update conversation title based on first message
        conversation.update_title_from_first_message()
        
        await db.commit()
    
    # Create response dict manually
    conv_dict = {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "is_archived": conversation.is_archived,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "message_count": 0,
        "last_message_at": conversation.created_at
    }
    
    return ConversationResponse.model_validate(conv_dict)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation with messages."""
    
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationDetail.model_validate(conversation)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation."""
    
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "Conversation deleted successfully"}


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a message to a conversation."""
    
    # Verify conversation exists and belongs to user
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        role=message_data.role,
        content=message_data.content,
        attachments=message_data.attachments,
        metadata=message_data.metadata
    )
    
    db.add(message)
    
    # Update conversation title if this is the first user message
    if message_data.role == "user" and not conversation.messages:
        conversation.update_title_from_first_message()
    
    await db.commit()
    await db.refresh(message)
    
    return MessageResponse.model_validate(message)


@router.post("/conversations/{conversation_id}/chat", response_model=ChatResponse)
async def chat(
    conversation_id: str,
    chat_data: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a chat message and get AI response."""
    
    # Verify conversation exists and belongs to user
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Add user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=chat_data.message,
        attachments=json.dumps(chat_data.attachments) if chat_data.attachments else None,
        metadata=json.dumps(chat_data.metadata) if chat_data.metadata else None
    )
    
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    # TODO: Process message with AI service and determine if generation is needed
    # For now, return a simple response
    requires_generation = "thumbnail" in chat_data.message.lower() or "generate" in chat_data.message.lower()
    
    return ChatResponse(
        message=MessageResponse.model_validate(user_message),
        conversation_id=conversation_id,
        requires_generation=requires_generation
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a conversation."""
    
    # Verify conversation exists and belongs to user
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    return [MessageResponse.model_validate(msg) for msg in messages]
