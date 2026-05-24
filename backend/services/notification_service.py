from typing import Dict, List
from datetime import datetime
from sqlalchemy.orm import Session

class NotificationService:
    """Service for handling notifications"""
    
    def __init__(self):
        self.notifications_queue: List[Dict] = []
    
    def create_notification(
        self,
        user_id: int,
        type: str,
        title: str,
        message: str,
        metadata: Dict = None
    ) -> Dict:
        """Create a new notification"""
        notification = {
            "user_id": user_id,
            "type": type,  # 'fraud', 'trade', 'deposit', 'withdrawal', 'system'
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
            "read": False
        }
        self.notifications_queue.append(notification)
        return notification
    
    def create_fraud_alert(
        self,
        user_id: int,
        fraud_type: str,
        risk_level: str,
        details: Dict
    ) -> Dict:
        """Create a fraud alert notification"""
        return self.create_notification(
            user_id=user_id,
            type="fraud",
            title=f"⚠️ {fraud_type.upper()} DETECTED",
            message=f"Suspicious activity detected: {details.get('description', fraud_type)}",
            metadata={
                "fraud_type": fraud_type,
                "risk_level": risk_level,
                "details": details
            }
        )
    
    def create_trade_notification(
        self,
        user_id: int,
        symbol: str,
        action: str,
        quantity: float,
        price: float
    ) -> Dict:
        """Create a trade notification"""
        return self.create_notification(
            user_id=user_id,
            type="trade",
            title=f"{action.upper()} {symbol}",
            message=f"You successfully {action.lower()}ed {quantity} shares of {symbol} at ₹{price}",
            metadata={
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "price": price
            }
        )
    
    def create_deposit_notification(
        self,
        user_id: int,
        amount: float
    ) -> Dict:
        """Create a deposit notification"""
        return self.create_notification(
            user_id=user_id,
            type="deposit",
            title="💰 DEPOSIT RECEIVED",
            message=f"₹{amount:,.2f} has been credited to your account",
            metadata={
                "amount": amount,
                "transaction_type": "deposit"
            }
        )
    
    def create_withdrawal_notification(
        self,
        user_id: int,
        amount: float,
        status: str = "pending"
    ) -> Dict:
        """Create a withdrawal notification"""
        status_msg = "Your withdrawal request has been received" if status == "pending" else "Your withdrawal has been processed"
        return self.create_notification(
            user_id=user_id,
            type="withdrawal",
            title="💸 WITHDRAWAL",
            message=f"{status_msg}. Amount: ₹{amount:,.2f}",
            metadata={
                "amount": amount,
                "transaction_type": "withdrawal",
                "status": status
            }
        )
    
    def get_notifications_for_user(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent notifications for a user"""
        user_notifications = [
            n for n in self.notifications_queue
            if n["user_id"] == user_id
        ]
        return user_notifications[-limit:]
    
    def clear_user_notifications(self, user_id: int):
        """Clear all notifications for a user"""
        self.notifications_queue = [
            n for n in self.notifications_queue
            if n["user_id"] != user_id
        ]

notification_service = NotificationService()
