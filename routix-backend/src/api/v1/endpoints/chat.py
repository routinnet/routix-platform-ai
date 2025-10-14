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
    
    # Process message with AI service
    from src.services.ai_service import AIService
    ai_service = AIService()
    
    # Analyze the message to determine intent
    requires_generation = await _analyze_chat_intent(
        chat_data.message,
        ai_service
    )
    
    # Generate AI response
    assistant_response = await _generate_assistant_response(
        chat_data.message,
        requires_generation,
        ai_service
    )
    
    # Add assistant message
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_response,
        metadata=json.dumps({"requires_generation": requires_generation})
    )
    
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    return ChatResponse(
        message=MessageResponse.model_validate(assistant_message),
        conversation_id=conversation_id,
        requires_generation=requires_generation
    )


async def _analyze_chat_intent(message: str, ai_service: AIService) -> bool:
    """Analyze chat message to determine if thumbnail generation is needed."""
    
    message_lower = message.lower()
    
    # Keywords that indicate generation intent
    generation_keywords = [
        "create", "generate", "make", "design", "build",
        "thumbnail", "image", "picture", "visual",
        "need", "want", "can you", "please", "help me with"
    ]
    
    # Check for generation keywords
    has_generation_keyword = any(
        keyword in message_lower for keyword in generation_keywords
    )
    
    # More sophisticated intent detection with AI (if available)
    if ai_service.openai_client:
        try:
            response = ai_service.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intent classifier. Determine if the user wants to generate a thumbnail. Respond with only 'yes' or 'no'."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            intent = response.choices[0].message.content.strip().lower()
            return "yes" in intent
            
        except Exception as e:
            print(f"Error in AI intent detection: {e}")
            # Fall back to keyword-based detection
            return has_generation_keyword
    
    return has_generation_keyword


async def _generate_assistant_response(
    user_message: str,
    requires_generation: bool,
    ai_service: AIService
) -> str:
    """Generate appropriate assistant response."""
    
    if requires_generation:
        # Response for generation requests
        responses = [
            "I'd be happy to help you create a thumbnail! Could you provide more details about what you have in mind?",
            "Great! I can help you generate a thumbnail. What style and theme would you like?",
            "Let me help you create an amazing thumbnail! Tell me more about your vision.",
            "I'll assist you with thumbnail generation. What's the main message or theme you want to convey?"
        ]
        
        # Use AI to generate personalized response if available
        if ai_service.openai_client:
            try:
                response = ai_service.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant for a thumbnail generation platform. Respond warmly and help users clarify their thumbnail creation needs. Keep responses concise (2-3 sentences)."
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"Error generating AI response: {e}")
                # Fall back to template response
                import random
                return random.choice(responses)
        else:
            import random
            return random.choice(responses)
    else:
        # Response for general conversation
        if ai_service.openai_client:
            try:
                response = ai_service.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant for a thumbnail generation platform. Provide helpful information and guide users. Keep responses concise (2-3 sentences)."
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"Error generating AI response: {e}")
                return "I'm here to help you create amazing thumbnails! How can I assist you today?"
        else:
            return "I'm here to help you create amazing thumbnails! How can I assist you today?"


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
