# app/routes/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from app.websocket_manager import manager
from app.utils.auth import verify_token
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])


async def get_current_user_ws(token: str = Query(...)):
    """Verify WebSocket token and return user info"""
    try:
        user_data = verify_token(token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time messaging

    Expects:
    - user_id: The user's ID from the URL path
    - token: JWT token for authentication as query parameter

    Sends/Receives JSON messages with the following structure:
    {
        "type": "new_message|message_read|message_delivered|typing|match|notification",
        "data": {...}
    }
    """

    # Verify token before accepting connection
    try:
        user_data = await get_current_user_ws(token)

        # Verify the token user matches the URL user_id
        if user_data.get("user_id") != user_id:
            await websocket.close(code=1008, reason="User ID mismatch")
            return

    except Exception as e:
        logger.error(f"Authentication failed for user {user_id}: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Connect the user
    await manager.connect(user_id, websocket)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "data": {
                "user_id": user_id,
                "message": "Connected to WebSocket"
            }
        })

        # Listen for messages from the client
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                logger.info(f"Received from user {user_id}: {message}")

                # Handle different message types
                message_type = message.get("type")

                if message_type == "ping":
                    # Respond to ping with pong
                    await websocket.send_json({
                        "type": "pong",
                        "data": {"timestamp": message.get("data", {}).get("timestamp")}
                    })

                elif message_type == "typing":
                    # Forward typing indicator to the recipient
                    recipient_id = message.get("data", {}).get("recipient_id")
                    if recipient_id:
                        await manager.send_personal_message({
                            "type": "typing",
                            "data": {
                                "user_id": user_id,
                                "is_typing": message.get("data", {}).get("is_typing", True)
                            }
                        }, recipient_id)

                elif message_type == "message_delivered":
                    # Forward delivery confirmation to sender
                    sender_id = message.get("data", {}).get("sender_id")
                    if sender_id:
                        await manager.send_personal_message({
                            "type": "message_delivered",
                            "data": message.get("data", {})
                        }, sender_id)

                else:
                    # Echo back unknown message types for debugging
                    await websocket.send_json({
                        "type": "echo",
                        "data": message
                    })

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from user {user_id}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                })
            except Exception as e:
                logger.error(f"Error processing message from user {user_id}: {e}")

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected normally")
        manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id, websocket)


@router.get("/ws/online-users")
def get_online_users():
    """Get list of currently online users"""
    return {
        "online_users": manager.get_online_users(),
        "count": len(manager.get_online_users())
    }


@router.get("/ws/user/{user_id}/status")
def check_user_status(user_id: str):
    """Check if a specific user is online"""
    return {
        "user_id": user_id,
        "is_online": manager.is_user_online(user_id)
    }
