# app/crud/message.py
from app.config import get_db
from app.models.Message import Message
from app.crud.Match import update_match_conversation_status
import uuid
from datetime import datetime

def create_message(sender_id: str, receiver_id: str, content: str, match_id: str = None):
    session = get_db()
    message_id = str(uuid.uuid4())

    query = """
    CREATE (m:Message {
        message_id: $message_id,
        match_id: $match_id,
        sender_id: $sender_id,
        receiver_id: $receiver_id,
        content: $content,
        sent_at: $sent_at,
        is_read: false
    })
    RETURN m
    """

    result = session.run(query, {
        "message_id": message_id,
        "match_id": match_id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "content": content,
        "sent_at": datetime.utcnow().isoformat()
    })

    record = result.single()
    node = record["m"]

    # Update match conversation status if match_id provided
    if match_id:
        update_match_conversation_status(match_id, True)

        # Update last_message_at on the match
        update_query = """
        MATCH ()-[m:MATCHES {match_id: $match_id}]-()
        SET m.last_message_at = $last_message_at
        """
        session.run(update_query, {"match_id": match_id, "last_message_at": node["sent_at"]})

    return Message(
        message_id=node["message_id"],
        match_id=node.get("match_id"),
        sender_id=node["sender_id"],
        receiver_id=node["receiver_id"],
        content=node["content"],
        sent_at=node["sent_at"],
        read_at=node.get("read_at"),
        is_read=node["is_read"]
    )

def get_message_by_id(message_id: str):
    session = get_db()
    query = "MATCH (m:Message {message_id: $message_id}) RETURN m"
    result = session.run(query, {"message_id": message_id}).single()

    if not result:
        return None

    node = result["m"]
    return Message(
        message_id=node["message_id"],
        match_id=node["match_id"],
        sender_id=node["sender_id"],
        receiver_id=node["receiver_id"],
        content=node["content"],
        sent_at=node["sent_at"],
        read_at=node.get("read_at"),
        is_read=node["is_read"]
    )

def get_match_messages(match_id: str, limit: int = 50, offset: int = 0):
    session = get_db()
    query = """
    MATCH (m:Message {match_id: $match_id})
    RETURN m
    ORDER BY m.sent_at DESC
    SKIP $offset
    LIMIT $limit
    """
    results = session.run(query, {"match_id": match_id, "offset": offset, "limit": limit})

    messages = []
    for record in results:
        node = record["m"]
        messages.append(Message(
            message_id=node["message_id"],
            match_id=node["match_id"],
            sender_id=node["sender_id"],
            receiver_id=node["receiver_id"],
            content=node["content"],
            sent_at=node["sent_at"],
            read_at=node.get("read_at"),
            is_read=node["is_read"]
        ))

    return messages

def mark_message_as_read(message_id: str):
    session = get_db()
    query = """
    MATCH (m:Message {message_id: $message_id})
    SET m.is_read = true, m.read_at = $read_at
    RETURN m
    """
    result = session.run(query, {
        "message_id": message_id,
        "read_at": datetime.utcnow().isoformat()
    }).single()

    if not result:
        return None

    node = result["m"]
    return Message(
        message_id=node["message_id"],
        match_id=node["match_id"],
        sender_id=node["sender_id"],
        receiver_id=node["receiver_id"],
        content=node["content"],
        sent_at=node["sent_at"],
        read_at=node.get("read_at"),
        is_read=node["is_read"]
    )

def get_unread_message_count(user_id: str):
    session = get_db()
    query = """
    MATCH (m:Message {receiver_id: $user_id, is_read: false})
    RETURN count(m) as unread_count
    """
    result = session.run(query, {"user_id": user_id}).single()

    return result["unread_count"]

def get_messages_between_users(user_id1: str, user_id2: str, limit: int = 50):
    """Get all messages between two users"""
    session = get_db()
    query = """
    MATCH (m:Message)
    WHERE (m.sender_id = $user_id1 AND m.receiver_id = $user_id2)
       OR (m.sender_id = $user_id2 AND m.receiver_id = $user_id1)
    RETURN m
    ORDER BY m.sent_at ASC
    LIMIT $limit
    """
    results = session.run(query, {"user_id1": user_id1, "user_id2": user_id2, "limit": limit})

    messages = []
    for record in results:
        node = record["m"]
        messages.append(Message(
            message_id=node["message_id"],
            match_id=node.get("match_id"),
            sender_id=node["sender_id"],
            receiver_id=node["receiver_id"],
            content=node["content"],
            sent_at=node["sent_at"],
            read_at=node.get("read_at"),
            is_read=node["is_read"]
        ))

    return messages
