# app/routes/message.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app import crud
from app.schemas.Message import MessageCreate, MessageResponse, ConversationResponse
from app.websocket_manager import manager
from typing import List
import asyncio

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("/", response_model=MessageResponse)
async def send_message(message: MessageCreate, background_tasks: BackgroundTasks):
    """Send a message between matched users"""
    # Verify both users exist
    sender = crud.user.get_user_by_id(message.sender_id)
    receiver = crud.user.get_user_by_id(message.receiver_id)

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    # Create message (match_id is optional)
    new_message = crud.Message.create_message(
        message.sender_id,
        message.receiver_id,
        message.content,
        message.match_id if hasattr(message, 'match_id') else None
    )

    # Send message via WebSocket to the receiver
    await manager.send_personal_message(
        {
            "type": "new_message",
            "data": {
                "message_id": new_message.message_id,
                "sender_id": new_message.sender_id,
                "receiver_id": new_message.receiver_id,
                "content": new_message.content,
                "sent_at": new_message.sent_at,
                "sender_name": sender.name
            }
        },
        message.receiver_id
    )

    return new_message.__dict__

@router.get("/{message_id}", response_model=MessageResponse)
def get_message(message_id: str):
    message = crud.Message.get_message_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message.__dict__

@router.get("/match/{match_id}")
def get_match_messages(match_id: str, limit: int = 50, offset: int = 0):
    """Get all messages in a match"""
    match = crud.Match.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    messages = crud.Message.get_match_messages(match_id, limit, offset)

    return {
        "match_id": match_id,
        "messages": [msg.__dict__ for msg in messages],
        "total_count": len(messages)
    }

@router.patch("/{message_id}/read", response_model=MessageResponse)
async def mark_message_read(message_id: str):
    """Mark a message as read"""
    message = crud.Message.mark_message_as_read(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Notify sender via WebSocket that message was read
    await manager.send_personal_message(
        {
            "type": "message_read",
            "data": {
                "message_id": message.message_id,
                "read_at": message.read_at
            }
        },
        message.sender_id
    )

    return message.__dict__

@router.get("/unread/{user_id}")
def get_unread_count(user_id: str):
    """Get count of unread messages for a user"""
    count = crud.Message.get_unread_message_count(user_id)
    return {"user_id": user_id, "unread_count": count}

@router.get("/{user_id}/conversations")
def get_user_conversations(user_id: str):
    """Get all conversations for a user (list of matches with last message)"""
    # Get all matches for the user
    matches = crud.Match.get_user_matches(user_id)

    conversations = []
    for match in matches:
        other_user_id = match["user_id"]  # Fixed: match returns "user_id" not "other_user_id"
        other_user = crud.user.get_user_by_id(other_user_id)

        if not other_user:
            continue

        # Get last message between these users
        try:
            messages = crud.Message.get_messages_between_users(user_id, other_user_id, limit=1)
            last_message = messages[0] if messages else None
        except:
            last_message = None

        # Get user's primary photo
        try:
            from app.crud import Photo as crud_photo_module
            photos = crud_photo_module.get_user_photos(other_user_id)
            primary_photo = next((p for p in photos if p.is_primary), photos[0] if photos else None)
            photo_url = primary_photo.url if primary_photo else None
        except:
            photo_url = None

        conversations.append({
            "conversation_id": match["match_id"],
            "user_id": other_user_id,
            "name": other_user.name,
            "photo": photo_url,
            "last_message": last_message.content if last_message else None,
            "last_message_time": last_message.sent_at if last_message else match["matched_at"],
            "unread_count": 0  # Can be implemented later
        })

    # Sort by last message time
    conversations.sort(key=lambda x: x["last_message_time"] or "", reverse=True)

    return conversations

@router.get("/{user_id1}/{user_id2}")
def get_messages_between_users(user_id1: str, user_id2: str, limit: int = 50):
    """Get all messages between two users"""
    messages = crud.Message.get_messages_between_users(user_id1, user_id2, limit)
    return [msg.__dict__ for msg in messages]

@router.post("/{user_id}/mark-conversation-read/{other_user_id}")
def mark_conversation_read(user_id: str, other_user_id: str):
    """Mark all messages in a conversation as read"""
    count = crud.Message.mark_conversation_as_read(user_id, other_user_id)
    return {"message": f"Marked {count} messages as read"}

@router.post("/{message_id}/delivered")
async def mark_message_delivered(message_id: str):
    """Mark a message as delivered"""
    message = crud.Message.mark_message_as_delivered(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Notify sender via WebSocket that message was delivered
    await manager.send_personal_message(
        {
            "type": "message_delivered",
            "data": {
                "message_id": message.message_id,
                "delivered_at": message.delivered_at
            }
        },
        message.sender_id
    )

    return {"message": "Message marked as delivered"}
