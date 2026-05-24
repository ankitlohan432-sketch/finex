from websocket import manager, ConnectionManager
from typing import Dict, Optional
import json

class SocketService:
    """Service for WebSocket operations"""
    
    def __init__(self):
        self.manager = manager
    
    async def broadcast_market_update(self, stock_data: Dict):
        """Broadcast stock market update to all connected clients"""
        message = {
            "type": "market_update",
            "data": stock_data
        }
        await self.manager.broadcast(message)
    
    async def broadcast_fraud_alert(self, alert_data: Dict):
        """Broadcast fraud alert to all admin clients"""
        message = {
            "type": "fraud_alert",
            "data": alert_data
        }
        await self.manager.broadcast(message)
    
    async def notify_user(self, user_id: str, notification: Dict):
        """Send notification to specific user"""
        message = {
            "type": "notification",
            "data": notification
        }
        await self.manager.send_to_user(user_id, message)
    
    async def broadcast_connection_stats(self):
        """Broadcast current connection statistics"""
        stats = self.manager.get_connection_stats()
        message = {
            "type": "connection_stats",
            "data": stats
        }
        await self.manager.broadcast(message)
    
    async def broadcast_trade_alert(self, trade_data: Dict):
        """Broadcast trade alert"""
        message = {
            "type": "trade_alert",
            "data": trade_data
        }
        await self.manager.broadcast(message)
    
    def get_active_connections_count(self) -> int:
        """Get count of active connections"""
        return len(self.manager.active_connections)
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        return self.manager.get_connection_stats()

socket_service = SocketService()
