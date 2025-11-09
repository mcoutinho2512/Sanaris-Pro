from sqlalchemy import Column, String, Boolean, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum
import uuid

class ChannelType(str, enum.Enum):
    DIRECT = "direct"
    GROUP = "group"
    SECTOR = "sector"

class MessageType(str, enum.Enum):
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    SYSTEM = "system"

class ChatChannel(Base):
    __tablename__ = "chat_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    channel_type = Column(SQLEnum(ChannelType), nullable=False, default=ChannelType.GROUP)
    sector = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    participants = relationship("ChatParticipant", back_populates="channel", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="channel", cascade="all, delete-orphan")
    created_by = relationship("User", foreign_keys=[created_by_id])

class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("chat_channels.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    last_read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    channel = relationship("ChatChannel", back_populates="participants")
    user = relationship("User")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("chat_channels.id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message_type = Column(SQLEnum(MessageType), nullable=False, default=MessageType.TEXT)
    content = Column(Text, nullable=False)
    file_url = Column(String(500))
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    channel = relationship("ChatChannel", back_populates="messages")
    sender = relationship("User")
    read_status = relationship("ChatReadStatus", back_populates="message", cascade="all, delete-orphan")

class ChatReadStatus(Base):
    __tablename__ = "chat_read_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    message = relationship("ChatMessage", back_populates="read_status")
    user = relationship("User")
