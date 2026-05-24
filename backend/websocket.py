from fastapi import WebSocket
from typing import List, Set
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: dict = {}
        self.connection_count = 0

    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_count += 1
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        
        print(f"Client connected. Active connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
        
        print(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting: {e}")

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all connections of a specific user"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending to user: {e}")

    def get_connection_stats(self):
        """Get current connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "total_connections": self.connection_count,
            "timestamp": datetime.utcnow().isoformat()
        }

manager = ConnectionManager()

from typing import Optional
