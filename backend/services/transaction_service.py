"""
Transaction Service
Handles all buy/sell transactions and fraud detection
"""

from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    DIVIDEND = "dividend"

class FraudSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TransactionService:
    """Service for handling all transactions and fraud detection"""
    
    def __init__(self):
        self.transaction_history = []
        self.fraud_alerts = []
        
    async def create_transaction(self, user_id: int, tx_type: TransactionType, 
                                 amount: float, symbol: str = None, 
                                 quantity: float = None, price: float = None):
        """
        Create a new transaction
        Checks for fraud before processing
        """
        
        # Fraud check first
        fraud_check = self.check_fraud(user_id, amount, symbol)
        
        transaction = {
            "id": len(self.transaction_history) + 1,
            "user_id": user_id,
            "type": tx_type,
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "amount": amount,
            "status": "pending" if fraud_check["is_flagged"] else "completed",
            "is_fraud_flagged": fraud_check["is_flagged"],
            "fraud_reason": fraud_check["reason"],
            "description": self.generate_description(tx_type, symbol, quantity, price),
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.transaction_history.append(transaction)
        
        if fraud_check["is_flagged"]:
            self.create_fraud_alert(user_id, transaction, fraud_check)
        
        return transaction
    
    def check_fraud(self, user_id: int, amount: float, symbol: str = None) -> dict:
        """
        Advanced fraud detection
        Returns fraud check results
        """
        
        fraud_indicators = []
        is_flagged = False
        severity = FraudSeverity.LOW
        
        # Check 1: Unusually large transaction
        if amount > 50000:
            fraud_indicators.append("Large transaction amount")
            severity = FraudSeverity.MEDIUM
        
        # Check 2: Multiple transactions in short time
        recent_txs = [
            tx for tx in self.transaction_history 
            if tx["user_id"] == user_id and 
            self.time_diff_seconds(tx["created_at"]) < 300  # Last 5 minutes
        ]
        if len(recent_txs) > 5:
            fraud_indicators.append("Multiple rapid transactions")
            severity = FraudSeverity.HIGH
            is_flagged = True
        
        # Check 3: Unusual time (3 AM - 5 AM)
        hour = datetime.utcnow().hour
        if hour >= 3 and hour <= 5:
            fraud_indicators.append("Unusual transaction time")
            severity = FraudSeverity.LOW
        
        # Check 4: Suspicious symbols (penny stocks, etc)
        if symbol and symbol.startswith("PENNY_"):
            fraud_indicators.append("High-risk stock symbol")
            severity = FraudSeverity.MEDIUM
        
        # Check 5: Pattern matching (same amount twice in a day)
        same_amount_txs = [
            tx for tx in self.transaction_history
            if tx["user_id"] == user_id and 
            tx["amount"] == amount and
            self.time_diff_seconds(tx["created_at"]) < 86400  # Last 24 hours
        ]
        if len(same_amount_txs) > 0:
            fraud_indicators.append("Duplicate transaction amount")
            severity = FraudSeverity.MEDIUM
        
        return {
            "is_flagged": is_flagged,
            "severity": severity.value,
            "indicators": fraud_indicators,
            "reason": " | ".join(fraud_indicators) if fraud_indicators else None
        }
    
    def create_fraud_alert(self, user_id: int, transaction: dict, fraud_check: dict):
        """Create a fraud alert for investigation"""
        alert = {
            "id": len(self.fraud_alerts) + 1,
            "user_id": user_id,
            "alert_type": "transaction",
            "severity": fraud_check["severity"],
            "description": f"Fraudulent transaction detected: {fraud_check['reason']}",
            "transaction_id": transaction["id"],
            "is_resolved": False,
            "created_at": datetime.utcnow().isoformat()
        }
        self.fraud_alerts.append(alert)
        print(f"🚨 FRAUD ALERT #{alert['id']}: {alert['description']}")
        return alert
    
    def generate_description(self, tx_type: TransactionType, symbol: str = None, 
                            quantity: float = None, price: float = None) -> str:
        """Generate human-readable transaction description"""
        
        if tx_type == TransactionType.BUY:
            return f"Bought {quantity} shares of {symbol} @ ${price:.2f}"
        elif tx_type == TransactionType.SELL:
            return f"Sold {quantity} shares of {symbol} @ ${price:.2f}"
        elif tx_type == TransactionType.DEPOSIT:
            return f"Deposited funds"
        elif tx_type == TransactionType.WITHDRAWAL:
            return f"Withdrew funds"
        elif tx_type == TransactionType.DIVIDEND:
            return f"Dividend received from {symbol}"
        return "Transaction"
    
    def time_diff_seconds(self, timestamp: str) -> int:
        """Calculate seconds since timestamp"""
        try:
            tx_time = datetime.fromisoformat(timestamp)
            return int((datetime.utcnow() - tx_time).total_seconds())
        except:
            return 0
    
    async def get_user_transactions(self, user_id: int, limit: int = 50):
        """Get recent transactions for a user"""
        return [
            tx for tx in self.transaction_history 
            if tx["user_id"] == user_id
        ][-limit:]
    
    async def get_transaction_stats(self, user_id: int):
        """Get transaction statistics"""
        user_txs = [tx for tx in self.transaction_history if tx["user_id"] == user_id]
        
        buy_txs = [tx for tx in user_txs if tx["type"] == "buy"]
        sell_txs = [tx for tx in user_txs if tx["type"] == "sell"]
        
        total_spent = sum(tx["amount"] for tx in buy_txs)
        total_received = sum(tx["amount"] for tx in sell_txs)
        fraud_flagged = sum(1 for tx in user_txs if tx["is_fraud_flagged"])
        
        return {
            "total_transactions": len(user_txs),
            "total_buys": len(buy_txs),
            "total_sells": len(sell_txs),
            "total_spent": total_spent,
            "total_received": total_received,
            "fraud_flagged_count": fraud_flagged,
            "success_rate": ((len(user_txs) - fraud_flagged) / len(user_txs) * 100) if user_txs else 0
        }
    
    async def resolve_fraud_alert(self, alert_id: int, action: str = "approve"):
        """Resolve a fraud alert (approve/reject transaction)"""
        for alert in self.fraud_alerts:
            if alert["id"] == alert_id:
                alert["is_resolved"] = True
                alert["resolved_action"] = action
                alert["resolved_at"] = datetime.utcnow().isoformat()
                
                # Update transaction status
                for tx in self.transaction_history:
                    if tx["id"] == alert["transaction_id"]:
                        if action == "approve":
                            tx["status"] = "completed"
                            tx["is_fraud_flagged"] = False
                        elif action == "reject":
                            tx["status"] = "failed"
                
                return alert
        return None
    
    async def get_fraud_alerts(self, user_id: int = None):
        """Get all fraud alerts"""
        if user_id:
            return [a for a in self.fraud_alerts if a["user_id"] == user_id]
        return self.fraud_alerts

# Export service
transaction_service = TransactionService()
