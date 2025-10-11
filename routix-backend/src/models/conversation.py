from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False, default="New Conversation")
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    generations = relationship("Generation", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title}, user_id={self.user_id})>"

    def get_message_count(self) -> int:
        """Get the number of messages in this conversation."""
        return len(self.messages) if self.messages else 0

    def get_last_message_at(self) -> datetime:
        """Get the timestamp of the last message."""
        if self.messages:
            return max(msg.created_at for msg in self.messages)
        return self.created_at

    def update_title_from_first_message(self):
        """Update conversation title based on first user message."""
        if self.messages:
            first_user_message = next(
                (msg for msg in self.messages if msg.role == "user"), 
                None
            )
            if first_user_message and first_user_message.content:
                # Take first 50 characters as title
                self.title = first_user_message.content[:50] + ("..." if len(first_user_message.content) > 50 else "")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    attachments = Column(Text, nullable=True)  # JSON string for file attachments
    message_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"

    @property
    def is_user_message(self) -> bool:
        """Check if this is a user message."""
        return self.role == "user"

    @property
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message."""
        return self.role == "assistant"

    @property
    def has_attachments(self) -> bool:
        """Check if this message has attachments."""
        return self.attachments is not None and self.attachments.strip() != ""
