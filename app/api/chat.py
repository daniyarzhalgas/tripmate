from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_user_from_websocket_token
from app.core.database import get_db, AsyncSessionLocal
from app.models.user import User
from app.schemas.chat import (
    ApiMessageResponse,
    ChatGroupResponse,
    ChatMemberResponse,
    MessageResponse,
    MessageSendRequest,
)
from app.services.chat_service import ChatService
from app.api.websocket_manager import manager
import json
from datetime import datetime

router = APIRouter(prefix="/chats", tags=["Chats"])


# ============= CHAT GROUP OPERATIONS =============
@router.get("/my-groups", response_model=List[ChatGroupResponse])
async def get_my_chat_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all chat groups the current user is a member of."""
    chat_service = ChatService(db)
    chat_groups = await chat_service.get_my_chat_groups(current_user.id, skip, limit)
    return chat_groups


@router.get("/{chat_group_id}", response_model=ChatGroupResponse)
async def get_chat_group(
    chat_group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get chat group by ID. User must be a member."""
    chat_service = ChatService(db)

    success, chat_group, error = await chat_service.get_chat_group(
        chat_group_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return chat_group


@router.get("/trip-vacancy/{trip_vacancy_id}", response_model=ChatGroupResponse)
async def get_chat_group_by_trip_vacancy(
    trip_vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get chat group for a trip vacancy. User must be a member."""
    chat_service = ChatService(db)

    success, chat_group, error = await chat_service.get_chat_group_by_trip_vacancy(
        trip_vacancy_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return chat_group


# ============= CHAT MEMBER OPERATIONS =============
@router.get("/{chat_group_id}/members", response_model=List[ChatMemberResponse])
async def get_chat_members(
    chat_group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all members of a chat group. User must be a member."""
    chat_service = ChatService(db)

    success, members, error = await chat_service.get_chat_members(
        chat_group_id, current_user.id, skip, limit
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return members


# ============= MESSAGE OPERATIONS =============
@router.post(
    "/{chat_group_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    chat_group_id: int,
    request: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to a chat group. User must be a member."""
    chat_service = ChatService(db)

    success, message, error = await chat_service.send_message(
        chat_group_id, current_user.id, request.content
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return message


@router.get("/{chat_group_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    chat_group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get messages from a chat group. User must be a member."""
    chat_service = ChatService(db)

    success, messages, error = await chat_service.get_messages(
        chat_group_id, current_user.id, skip, limit
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return messages


@router.get("/{chat_group_id}/messages/recent", response_model=List[MessageResponse])
async def get_recent_messages(
    chat_group_id: int,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent messages from a chat group. User must be a member."""
    chat_service = ChatService(db)

    success, messages, error = await chat_service.get_recent_messages(
        chat_group_id, current_user.id, limit
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return messages


@router.delete(
    "/{chat_group_id}/messages/{message_id}", response_model=ApiMessageResponse
)
async def delete_message(
    chat_group_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a message. Only the sender can delete their own message."""
    chat_service = ChatService(db)

    success, error = await chat_service.delete_message(message_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return ApiMessageResponse(message="Message deleted successfully")


# ============= WEBSOCKET OPERATIONS =============
@router.websocket("/ws/{chat_group_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    chat_group_id: int,
    token: str,
):
    """
    WebSocket endpoint for real-time chat.

    Connect with: ws://host/api/v1/chats/ws/{chat_group_id}?token=YOUR_JWT_TOKEN

    Message types to send:
    - {"type": "message", "content": "Hello!"} - Send a message
    - {"type": "typing", "is_typing": true/false} - Send typing indicator

    Message types received:
    - {"type": "connection", "status": "connected"} - Connection established
    - {"type": "message", ...} - New message from another user
    - {"type": "typing", "user_id": 123, "is_typing": true} - Typing indicator
    - {"type": "error", "message": "..."} - Error message
    - {"type": "user_joined", "user_id": 123} - User joined the chat
    - {"type": "user_left", "user_id": 123} - User left the chat
    """
    authenticated_user = None
    user_id = None

    try:
        # Authenticate user and verify membership using a separate session
        async with AsyncSessionLocal() as db:
            # Authenticate user
            authenticated_user = await get_user_from_websocket_token(token, db)
            if not authenticated_user:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Invalid authentication",
                )
                return

            user_id = authenticated_user.id

            # Verify user is a member of the chat group
            chat_service = ChatService(db)
            success, chat_group, error = await chat_service.get_chat_group(
                chat_group_id, user_id
            )

            if not success:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason=error or "Access denied",
                )
                return

        # Connect to WebSocket
        await manager.connect(websocket, chat_group_id, user_id)

        # Notify other users that this user joined
        await manager.broadcast_to_chat_group(
            chat_group_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
            exclude=websocket,
        )

        # Handle incoming messages
        while True:
            # Receive message from WebSocket
            data = await websocket.receive_text()
            message_data = json.loads(data)

            message_type = message_data.get("type")

            if message_type == "message":
                # Handle chat message
                content = message_data.get("content", "").strip()
                if not content:
                    continue

                # Save message to database using a new session for each operation
                async with AsyncSessionLocal() as db:
                    chat_service = ChatService(db)
                    success, saved_message, error = await chat_service.send_message(
                        chat_group_id, user_id, content
                    )
                    await db.commit()

                if success and saved_message:
                    # Broadcast message to all connected users
                    broadcast_data = {
                        "type": "message",
                        "id": saved_message.id,
                        "chat_group_id": saved_message.chat_group_id,
                        "sender_id": saved_message.sender_id,
                        "content": saved_message.content,
                        "created_at": saved_message.created_at.isoformat(),
                    }
                    await manager.broadcast_to_chat_group(chat_group_id, broadcast_data)
                else:
                    # Send error back to sender
                    await manager.send_personal_message(
                        {"type": "error", "message": error or "Failed to send message"},
                        websocket,
                    )

            elif message_type == "typing":
                # Handle typing indicator
                is_typing = message_data.get("is_typing", False)
                await manager.send_typing_indicator(chat_group_id, user_id, is_typing)

            else:
                # Unknown message type
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        # Handle disconnection
        if authenticated_user:
            manager.disconnect(websocket, chat_group_id)
            # Notify other users that this user left
            await manager.broadcast_to_chat_group(
                chat_group_id,
                {
                    "type": "user_left",
                    "user_id": authenticated_user.id,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

    except Exception as e:
        # Handle any other errors
        if authenticated_user:
            manager.disconnect(websocket, chat_group_id)
            try:
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=str(e))
            except:
                pass


@router.get("/{chat_group_id}/active-users", response_model=List[int])
async def get_active_users(
    chat_group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of currently active user IDs in a chat group via WebSocket."""
    chat_service = ChatService(db)

    # Verify user is a member
    success, _, error = await chat_service.get_chat_group(
        chat_group_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    # Get active users from WebSocket manager
    active_users = manager.get_active_users(chat_group_id)
    return active_users
