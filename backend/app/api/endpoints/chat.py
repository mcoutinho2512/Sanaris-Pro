from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.chat import ChatChannel, ChatMessage, ChatParticipant, ChatReadStatus, ChannelType, MessageType
from app.models.user import User
from app.schemas.chat import (
    ChatChannelCreate, ChatChannelUpdate, ChatChannelResponse,
    ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse,
    ChatParticipantAdd, ChatParticipantResponse, UserInfo
)
from app.core.security import get_current_user
from app.core.websocket_manager import manager

router = APIRouter()

# ==================== CHANNELS ====================

@router.post("/channels", response_model=ChatChannelResponse)
def create_channel(
    channel_data: ChatChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo canal de chat"""
    
    # Criar canal
    new_channel = ChatChannel(
        organization_id=current_user.organization_id if hasattr(current_user, "organization_id") else db.query(User).filter(User.id == current_user.id).first().organization_id,
        name=channel_data.name,
        description=channel_data.description,
        channel_type=channel_data.channel_type,
        sector=channel_data.sector,
        created_by_id=current_user.id
    )
    db.add(new_channel)
    db.flush()
    
    # Adicionar criador como participante admin
    creator_participant = ChatParticipant(
        channel_id=new_channel.id,
        user_id=current_user.id,
        is_admin=True
    )
    db.add(creator_participant)
    
    # Adicionar outros participantes
    for user_id in channel_data.participant_ids:
        if user_id != current_user.id:
            participant = ChatParticipant(
                channel_id=new_channel.id,
                user_id=user_id,
                is_admin=False
            )
            db.add(participant)
    
    db.commit()
    db.refresh(new_channel)
    
    return ChatChannelResponse(
        id=new_channel.id,
        organization_id=new_channel.organization_id,
        name=new_channel.name,
        description=new_channel.description,
        channel_type=new_channel.channel_type,
        sector=new_channel.sector,
        is_active=new_channel.is_active,
        created_by_id=new_channel.created_by_id,
        created_at=new_channel.created_at,
        unread_count=0
    )

@router.get("/channels", response_model=List[ChatChannelResponse])
def list_channels(
    channel_type: Optional[ChannelType] = None,
    sector: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar canais do usuário"""
    
    query = db.query(ChatChannel).join(ChatParticipant).filter(
        and_(
            ChatChannel.organization_id == current_user.organization_id,
            ChatParticipant.user_id == current_user.id,
            ChatChannel.is_active == True
        )
    )
    
    if channel_type:
        query = query.filter(ChatChannel.channel_type == channel_type)
    
    if sector:
        query = query.filter(ChatChannel.sector == sector)
    
    channels = query.offset(skip).limit(limit).all()
    
    # Calcular mensagens não lidas e última mensagem
    result = []
    for channel in channels:
        # Pegar última leitura do usuário
        participant = db.query(ChatParticipant).filter(
            and_(
                ChatParticipant.channel_id == channel.id,
                ChatParticipant.user_id == current_user.id
            )
        ).first()
        
        # Contar mensagens não lidas
        unread_count = 0
        if participant and participant.last_read_at:
            unread_count = db.query(ChatMessage).filter(
                and_(
                    ChatMessage.channel_id == channel.id,
                    ChatMessage.created_at > participant.last_read_at,
                    ChatMessage.sender_id != current_user.id
                )
            ).count()
        else:
            unread_count = db.query(ChatMessage).filter(
                and_(
                    ChatMessage.channel_id == channel.id,
                    ChatMessage.sender_id != current_user.id
                )
            ).count()
        
        # Pegar última mensagem
        last_msg = db.query(ChatMessage).filter(
            ChatMessage.channel_id == channel.id
        ).order_by(ChatMessage.created_at.desc()).first()
        
        result.append(ChatChannelResponse(
            id=channel.id,
            organization_id=channel.organization_id,
            name=channel.name,
            description=channel.description,
            channel_type=channel.channel_type,
            sector=channel.sector,
            is_active=channel.is_active,
            created_by_id=channel.created_by_id,
            created_at=channel.created_at,
            unread_count=unread_count,
            last_message=last_msg.content if last_msg else None,
            last_message_at=last_msg.created_at if last_msg else None
        ))
    
    return result

@router.get("/channels/{channel_id}", response_model=ChatChannelResponse)
def get_channel(
    channel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter detalhes de um canal"""
    
    channel = db.query(ChatChannel).filter(
        and_(
            ChatChannel.id == channel_id,
            ChatChannel.organization_id == current_user.organization_id
        )
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Verificar se usuário é participante
    is_participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == current_user.id
        )
    ).first()
    
    if not is_participant:
        raise HTTPException(status_code=403, detail="Você não é participante deste canal")
    
    # Calcular mensagens não lidas
    unread_count = 0
    if is_participant.last_read_at:
        unread_count = db.query(ChatMessage).filter(
            and_(
                ChatMessage.channel_id == channel_id,
                ChatMessage.created_at > is_participant.last_read_at,
                ChatMessage.sender_id != current_user.id
            )
        ).count()
    else:
        unread_count = db.query(ChatMessage).filter(
            and_(
                ChatMessage.channel_id == channel_id,
                ChatMessage.sender_id != current_user.id
            )
        ).count()
    
    return ChatChannelResponse(
        id=channel.id,
        organization_id=channel.organization_id,
        name=channel.name,
        description=channel.description,
        channel_type=channel.channel_type,
        sector=channel.sector,
        is_active=channel.is_active,
        created_by_id=channel.created_by_id,
        created_at=channel.created_at,
        unread_count=unread_count
    )

@router.put("/channels/{channel_id}", response_model=ChatChannelResponse)
def update_channel(
    channel_id: UUID,
    channel_data: ChatChannelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar canal"""
    
    channel = db.query(ChatChannel).filter(
        and_(
            ChatChannel.id == channel_id,
            ChatChannel.organization_id == current_user.organization_id
        )
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Verificar se é admin
    is_admin = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        )
    ).first()
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar o canal")
    
    # Atualizar
    for field, value in channel_data.model_dump(exclude_unset=True).items():
        setattr(channel, field, value)
    
    db.commit()
    db.refresh(channel)
    
    return ChatChannelResponse(
        id=channel.id,
        organization_id=channel.organization_id,
        name=channel.name,
        description=channel.description,
        channel_type=channel.channel_type,
        sector=channel.sector,
        is_active=channel.is_active,
        created_by_id=channel.created_by_id,
        created_at=channel.created_at,
        unread_count=0
    )

@router.delete("/channels/{channel_id}")
def delete_channel(
    channel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar canal (soft delete)"""
    
    channel = db.query(ChatChannel).filter(
        and_(
            ChatChannel.id == channel_id,
            ChatChannel.organization_id == current_user.organization_id
        )
    ).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Verificar se é admin
    is_admin = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        )
    ).first()
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar o canal")
    
    channel.is_active = False
    db.commit()
    
    return {"message": "Canal deletado com sucesso"}

# ==================== MESSAGES ====================

@router.post("/messages", response_model=ChatMessageResponse)
async def send_message(
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enviar mensagem"""
    
    # Verificar se é participante
    is_participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == message_data.channel_id,
            ChatParticipant.user_id == current_user.id
        )
    ).first()
    
    if not is_participant:
        raise HTTPException(status_code=403, detail="Você não é participante deste canal")
    
    # Criar mensagem
    new_message = ChatMessage(
        channel_id=message_data.channel_id,
        sender_id=current_user.id,
        message_type=message_data.message_type,
        content=message_data.content,
        file_url=message_data.file_url
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Carregar sender info
    sender_info = UserInfo(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email
    )
    
    response = ChatMessageResponse(
        id=new_message.id,
        channel_id=new_message.channel_id,
        sender_id=new_message.sender_id,
        sender=sender_info,
        message_type=new_message.message_type,
        content=new_message.content,
        file_url=new_message.file_url,
        is_edited=new_message.is_edited,
        edited_at=new_message.edited_at,
        created_at=new_message.created_at,
        read_by=[]
    )
    
    # Broadcast via WebSocket
    await manager.broadcast_to_channel(
        {
            "type": "message",
            "data": response.model_dump(mode='json')
        },
        message_data.channel_id
    )
    
    return response

@router.get("/channels/{channel_id}/messages", response_model=List[ChatMessageResponse])
def get_messages(
    channel_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter mensagens de um canal"""
    
    # Verificar se é participante
    is_participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == current_user.id
        )
    ).first()
    
    if not is_participant:
        raise HTTPException(status_code=403, detail="Você não é participante deste canal")
    
    messages = db.query(ChatMessage).options(
        joinedload(ChatMessage.sender),
        joinedload(ChatMessage.read_status)
    ).filter(
        ChatMessage.channel_id == channel_id
    ).order_by(ChatMessage.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for msg in messages:
        sender_info = UserInfo(
            id=msg.sender.id,
            full_name=msg.sender.full_name,
            email=msg.sender.email
        )
        
        read_by = [rs.user_id for rs in msg.read_status]
        
        result.append(ChatMessageResponse(
            id=msg.id,
            channel_id=msg.channel_id,
            sender_id=msg.sender_id,
            sender=sender_info,
            message_type=msg.message_type,
            content=msg.content,
            file_url=msg.file_url,
            is_edited=msg.is_edited,
            edited_at=msg.edited_at,
            created_at=msg.created_at,
            read_by=read_by
        ))
    
    return list(reversed(result))  # Retornar em ordem cronológica

@router.put("/messages/{message_id}", response_model=ChatMessageResponse)
async def update_message(
    message_id: UUID,
    message_data: ChatMessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Editar mensagem"""
    
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você só pode editar suas próprias mensagens")
    
    message.content = message_data.content
    message.is_edited = True
    message.edited_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    sender_info = UserInfo(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email
    )
    
    response = ChatMessageResponse(
        id=message.id,
        channel_id=message.channel_id,
        sender_id=message.sender_id,
        sender=sender_info,
        message_type=message.message_type,
        content=message.content,
        file_url=message.file_url,
        is_edited=message.is_edited,
        edited_at=message.edited_at,
        created_at=message.created_at,
        read_by=[]
    )
    
    # Broadcast via WebSocket
    await manager.broadcast_to_channel(
        {
            "type": "message_updated",
            "data": response.model_dump(mode='json')
        },
        message.channel_id
    )
    
    return response

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar mensagem"""
    
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você só pode deletar suas próprias mensagens")
    
    channel_id = message.channel_id
    
    db.delete(message)
    db.commit()
    
    # Broadcast via WebSocket
    await manager.broadcast_to_channel(
        {
            "type": "message_deleted",
            "data": {"message_id": str(message_id)}
        },
        channel_id
    )
    
    return {"message": "Mensagem deletada com sucesso"}

@router.post("/channels/{channel_id}/read")
async def mark_as_read(
    channel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marcar canal como lido"""
    
    participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == current_user.id
        )
    ).first()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Você não é participante deste canal")
    
    participant.last_read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Canal marcado como lido"}

# ==================== PARTICIPANTS ====================

@router.post("/channels/{channel_id}/participants", response_model=ChatParticipantResponse)
def add_participant(
    channel_id: UUID,
    participant_data: ChatParticipantAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Adicionar participante ao canal"""
    
    # Verificar se é admin
    is_admin = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        )
    ).first()
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem adicionar participantes")
    
    # Verificar se já é participante
    existing = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == participant_data.user_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já é participante")
    
    # Adicionar
    new_participant = ChatParticipant(
        channel_id=channel_id,
        user_id=participant_data.user_id,
        is_admin=participant_data.is_admin
    )
    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    
    # Carregar user info
    user = db.query(User).filter(User.id == participant_data.user_id).first()
    user_info = UserInfo(
        id=user.id,
        full_name=user.full_name,
        email=user.email
    )
    
    return ChatParticipantResponse(
        id=new_participant.id,
        channel_id=new_participant.channel_id,
        user_id=new_participant.user_id,
        user=user_info,
        is_admin=new_participant.is_admin,
        is_muted=new_participant.is_muted,
        last_read_at=new_participant.last_read_at
    )

@router.get("/channels/{channel_id}/participants", response_model=List[ChatParticipantResponse])
def list_participants(
    channel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar participantes do canal"""
    
    # Verificar se é participante
    is_participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == current_user.id
        )
    ).first()
    
    if not is_participant:
        raise HTTPException(status_code=403, detail="Você não é participante deste canal")
    
    participants = db.query(ChatParticipant).options(
        joinedload(ChatParticipant.user)
    ).filter(ChatParticipant.channel_id == channel_id).all()
    
    result = []
    for p in participants:
        user_info = UserInfo(
            id=p.user.id,
            full_name=p.user.full_name,
            email=p.user.email
        )
        
        result.append(ChatParticipantResponse(
            id=p.id,
            channel_id=p.channel_id,
            user_id=p.user_id,
            user=user_info,
            is_admin=p.is_admin,
            is_muted=p.is_muted,
            last_read_at=p.last_read_at
        ))
    
    return result

@router.delete("/channels/{channel_id}/participants/{user_id}")
def remove_participant(
    channel_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remover participante do canal"""
    
    # Verificar se é admin
    is_admin = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == current_user.id,
            ChatParticipant.is_admin == True
        )
    ).first()
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem remover participantes")
    
    participant = db.query(ChatParticipant).filter(
        and_(
            ChatParticipant.channel_id == channel_id,
            ChatParticipant.user_id == user_id
        )
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    
    db.delete(participant)
    db.commit()
    
    return {"message": "Participante removido com sucesso"}

# ==================== WEBSOCKET ====================

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint para chat em tempo real"""
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "subscribe":
                # Subscribe to channel
                channel_id = UUID(data["channel_id"])
                await manager.subscribe_to_channel(user_id, channel_id)
                
            elif data["type"] == "unsubscribe":
                # Unsubscribe from channel
                channel_id = UUID(data["channel_id"])
                await manager.unsubscribe_from_channel(user_id, channel_id)
                
            elif data["type"] == "typing":
                # Typing indicator
                channel_id = UUID(data["channel_id"])
                user_name = data["user_name"]
                is_typing = data["is_typing"]
                await manager.broadcast_typing_indicator(channel_id, user_id, user_name, is_typing)
                
            elif data["type"] == "ping":
                # Keep alive
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# ========== NOVOS ENDPOINTS ==========

@router.delete("/channels/{channel_id}")
def delete_channel(
    channel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Excluir canal (apenas criador ou admin)"""
    
    channel = db.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Verificar permissão
    if channel.created_by_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Sem permissão para excluir este canal")
    
    # Soft delete
    from datetime import datetime
    channel.is_active = False
    db.commit()
    
    return {"message": "Canal excluído com sucesso"}


@router.post("/channels/{channel_id}/participants")
def add_participant(
    channel_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Adicionar participante ao canal"""
    
    channel = db.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Verificar se usuário existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se já é participante
    existing = db.query(ChatParticipant).filter(
        ChatParticipant.channel_id == channel_id,
        ChatParticipant.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já é participante")
    
    # Adicionar participante
    participant = ChatParticipant(
        channel_id=channel_id,
        user_id=user_id,
        role='member'
    )
    db.add(participant)
    
    # Criar mensagem de sistema
    system_msg = ChatMessage(
        channel_id=channel_id,
        sender_id=current_user.id,
        content=f"{user.full_name} foi adicionado(a) ao canal",
        message_type='system'
    )
    db.add(system_msg)
    
    db.commit()
    
    return {"message": "Participante adicionado com sucesso"}


@router.delete("/channels/{channel_id}/participants/{user_id}")
def remove_participant(
    channel_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remover participante do canal"""
    
    channel = db.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
    
    if not channel:
        raise HTTPException(status_code=404, detail="Canal não encontrado")
    
    # Verificar permissão (criador ou o próprio usuário pode sair)
    if channel.created_by_id != current_user.id and user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    # Remover participante
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.channel_id == channel_id,
        ChatParticipant.user_id == user_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    db.delete(participant)
    
    # Criar mensagem de sistema
    system_msg = ChatMessage(
        channel_id=channel_id,
        sender_id=current_user.id,
        content=f"{user.full_name} saiu do canal",
        message_type='system'
    )
    db.add(system_msg)
    
    db.commit()
    
    return {"message": "Participante removido com sucesso"}


@router.get("/channels/{channel_id}/participants")
def list_participants(
    channel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar participantes do canal"""
    
    participants = db.query(ChatParticipant).filter(
        ChatParticipant.channel_id == channel_id
    ).all()
    
    result = []
    for p in participants:
        user = db.query(User).filter(User.id == p.user_id).first()
        if user:
            result.append({
                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "role": p.role,
                "joined_at": p.joined_at.isoformat()
            })
    
    return result

@router.get("/channels/{channel_id}/files")
def list_channel_files(
    channel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar todos os arquivos de um canal"""
    
    # Buscar mensagens com arquivos
    messages = db.query(ChatMessage).filter(
        ChatMessage.channel_id == channel_id,
        ChatMessage.message_type.in_(['file', 'image'])
    ).order_by(ChatMessage.created_at.desc()).all()
    
    files = []
    for msg in messages:
        if msg.file_url:
            files.append({
                "id": str(msg.id),
                "file_name": msg.file_name or "Arquivo",
                "file_url": msg.file_url,
                "message_type": msg.message_type,
                "created_at": msg.created_at.isoformat(),
                "sender": {
                    "id": str(msg.sender.id),
                    "full_name": msg.sender.full_name
                }
            })
    
    return files
