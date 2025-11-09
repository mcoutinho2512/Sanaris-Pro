from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class ChannelType(str, Enum):
    DIRECT = "direct"
    GROUP = "group"
    SECTOR = "sector"

class MessageType(str, Enum):
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    SYSTEM = "system"

# Channel Schemas
class ChatChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    channel_type: ChannelType = ChannelType.GROUP
    sector: Optional[str] = None
    participant_ids: List[UUID] = Field(default_factory=list)

class ChatChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    sector: Optional[str] = None
    is_active: Optional[bool] = None

class ChatChannelResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str]
    channel_type: ChannelType
    sector: Optional[str]
    is_active: bool
    created_by_id: UUID
    created_at: datetime
    unread_count: int = 0
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Message Schemas
class ChatMessageCreate(BaseModel):
    channel_id: UUID
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.TEXT
    file_url: Optional[str] = None

class ChatMessageUpdate(BaseModel):
    content: str = Field(..., min_length=1)

class UserInfo(BaseModel):
    id: UUID
    full_name: str
    email: str

    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    id: UUID
    channel_id: UUID
    sender_id: UUID
    sender: UserInfo
    message_type: MessageType
    content: str
    file_url: Optional[str]
    is_edited: bool
    edited_at: Optional[datetime]
    created_at: datetime
    read_by: List[UUID] = Field(default_factory=list)

    class Config:
        from_attributes = True

# Participant Schemas
class ChatParticipantAdd(BaseModel):
    user_id: UUID
    is_admin: bool = False

class ChatParticipantResponse(BaseModel):
    id: UUID
    channel_id: UUID
    user_id: UUID
    user: UserInfo
    is_admin: bool
    is_muted: bool
    last_read_at: Optional[datetime]

    class Config:
        from_attributes = True

# WebSocket Schemas
class TypingIndicator(BaseModel):
    channel_id: UUID
    user_id: UUID
    user_name: str
    is_typing: bool

class OnlineStatus(BaseModel):
    user_id: UUID
    is_online: bool
    last_seen: datetime

class WebSocketMessage(BaseModel):
    type: str  # "message", "typing", "online_status", "read_receipt"
    data: dict
