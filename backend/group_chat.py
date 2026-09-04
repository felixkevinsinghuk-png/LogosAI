"""
Group Chat Module
Handles WebSocket connections and isolated room logic for the Group Chat feature.
Rooms are identified exclusively by a 6-character alphanumeric code.
"""

from typing import Dict, List, Optional, Union
import random
import string
from fastapi import WebSocket

MAX_PARTICIPANTS = 13

# In-memory registry for active rooms and their connections
# Structure: {
#   "A9X4K2": {
#      "clients": [WebSocket1, WebSocket2, ...],
#      "history": [{"name": "User1", "message": "hello!"}, ...],
#      "name": "Bible Study Group"
#   }
# }
_rooms: dict[str, dict] = {}


def generate_room_code() -> str:
    """
    Generates a unique 6-character uppercase alphanumeric room code.
    Ensures that the generated code does not already exist in active rooms.
    """
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(characters, k=6))
        if code not in _rooms:
            return code


def create_room(group_name: str) -> str:
    """
    Creates a new room with a unique code and initializes its state.
    Group name is mandatory.
    """
    code = generate_room_code()
    _rooms[code] = {
        "clients": [],
        "history": [],
        "name": group_name
    }
    return code


def validate_room(code: str) -> bool:
    """
    Checks if a room exists given an exactly 6-character alphanumeric string.
    """
    if not code or len(code) != 6 or not code.isalnum():
        return False
    # Case-insensitive check internally
    return code.upper() in _rooms


def get_room_info(code: str) -> Optional[dict]:
    """
    Returns information about the room including participant count.
    """
    code = code.upper()
    if code in _rooms:
        return {
            "name": _rooms[code]["name"],
            "participants": len(_rooms[code]["clients"]),
            "max": MAX_PARTICIPANTS
        }
    return None


class ConnectionManager:
    def __init__(self):
        pass

    async def connect(self, room_code: str, name: str, websocket: WebSocket):
        await websocket.accept()
        if room_code in _rooms:
            # Enforce 13 participant limit
            if len(_rooms[room_code]["clients"]) >= MAX_PARTICIPANTS:
                await websocket.close(code=1008, reason="Room has reached its maximum capacity of 13 participants.")
                return False

            _rooms[room_code]["clients"].append(websocket)
            
            # Send chat history to the newly connected user
            for msg in _rooms[room_code]["history"]:
                await websocket.send_json(msg)

            # Broadcast system message about join
            await self.broadcast_system(room_code, f"{name} joined the room")
            return True
        else:
            await websocket.close(code=1008, reason="Room does not exist.")
            return False

    async def disconnect(self, room_code: str, name: str, websocket: WebSocket):
        if room_code in _rooms:
            try:
                _rooms[room_code]["clients"].remove(websocket)
                # Broadcast system message about leave
                if len(_rooms[room_code]["clients"]) > 0:
                    await self.broadcast_system(room_code, f"{name} left the room")
            except ValueError:
                pass
            
            # Optional cleanup: remove room if empty
            # if not _rooms[room_code]["clients"]:
            #     del _rooms[room_code]

    async def broadcast_system(self, room_code: str, content: str):
        """Broadcasts a system notification (e.g., join/leave) with updated participant counts."""
        if room_code in _rooms:
            count = len(_rooms[room_code]["clients"])
            msg = {
                "type": "system",
                "message": content,
                "participants": count,
                "max": MAX_PARTICIPANTS
            }
            # We don't save system messages strictly to history, or maybe we do so latecomers see who arrived?
            # For now, we will save to history so latecomers see the flow
            _rooms[room_code]["history"].append(msg)
            
            for connection in _rooms[room_code]["clients"]:
                try:
                    await connection.send_json(msg)
                except Exception:
                    pass

    async def broadcast(self, room_code: str, message: dict):
        """
        Broadcasts a JSON message to all clients in the isolated room.
        Message dictionary must at least contain "name" and "message" keys.
        """
        if room_code in _rooms:
            # Inject type if standard message
            message["type"] = "chat"
            
            # Store message in history
            _rooms[room_code]["history"].append(message)
            
            # Keep history manageable (last 100 messages)
            if len(_rooms[room_code]["history"]) > 100:
                _rooms[room_code]["history"] = _rooms[room_code]["history"][-100:]
                
            # Broadcast to all clients in this isolated room
            for connection in list(_rooms[room_code]["clients"]):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    # Connection is dead, remove it
                    print(f"Error sending message to client in {room_code}, removing connection: {e}")
                    # Force a disconnect but without name resolution since we lost it here...
                    self._force_remove(room_code, connection)

    def _force_remove(self, room_code: str, websocket: WebSocket):
         if room_code in _rooms:
            try:
                _rooms[room_code]["clients"].remove(websocket)
            except ValueError:
                pass

manager = ConnectionManager()
