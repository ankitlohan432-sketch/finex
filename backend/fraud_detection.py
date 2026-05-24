from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict

class FraudDetectionEngine:
    def __init__(self):
        self.suspicious_patterns = defaultdict(list)
        self.blocked_ips = set()
        self.blocked_emails = set()
        self.transaction_history = defaultdict(list)

    def check_multiple_registrations(self, email: str, ip: str) -> Dict:
        """Check for multiple registrations from same IP/email"""
        risk_score = 0
        alerts = []
        
        # Check same email registrations in last 24 hours
        recent_same_email = len([
            t for t in self.suspicious_patterns[f"email:{email}"]
            if (datetime.utcnow() - t) < timedelta(hours=24)
        ])
        
        if recent_same_email > 3:
            risk_score += 0.3
            alerts.append(f"Multiple registrations from same email ({recent_same_email})")
        
        # Check same IP registrations in last 24 hours
        recent_same_ip = len([
            t for t in self.suspicious_patterns[f"ip:{ip}"]
            if (datetime.utcnow() - t) < timedelta(hours=24)
        ])
        
        if recent_same_ip > 10:
            risk_score += 0.4
            alerts.append(f"Multiple registrations from same IP ({recent_same_ip})")
        
        return {
            "risk_score": min(risk_score, 1.0),
            "is_suspicious": risk_score > 0.5,
            "alerts": alerts
        }

    def check_unusual_transaction(self, user_id: str, amount: float, transaction_type: str) -> Dict:
        """Check for unusual transaction patterns"""
        risk_score = 0
        alerts = []
        
        user_history = self.transaction_history[user_id]
        
        if user_history:
            avg_amount = sum(t["amount"] for t in user_history) / len(user_history)
            
            # Check for unusually large transaction
            if amount > avg_amount * 5:
                risk_score += 0.35
                alerts.append(f"Transaction amount {amount} is 5x higher than average")
        
        # Check for rapid multiple transactions
        recent_transactions = [
            t for t in user_history
            if (datetime.utcnow() - t["timestamp"]) < timedelta(minutes=5)
        ]
        
        if len(recent_transactions) > 5:
            risk_score += 0.3
            alerts.append(f"Rapid transactions detected ({len(recent_transactions)} in 5 mins)")
        
        self.transaction_history[user_id].append({
            "amount": amount,
            "type": transaction_type,
            "timestamp": datetime.utcnow()
        })
        
        return {
            "risk_score": min(risk_score, 1.0),
            "is_suspicious": risk_score > 0.5,
            "alerts": alerts
        }

    def log_suspicious_activity(self, user_id: str, activity_type: str, details: Dict):
        """Log suspicious activity"""
        self.suspicious_patterns[f"activity:{user_id}"].append({
            "type": activity_type,
            "details": details,
            "timestamp": datetime.utcnow()
        })

    def block_ip(self, ip: str):
        """Block an IP address"""
        self.blocked_ips.add(ip)

    def block_email(self, email: str):
        """Block an email address"""
        self.blocked_emails.add(email)

    def is_ip_blocked(self, ip: str) -> bool:
        return ip in self.blocked_ips

    def is_email_blocked(self, email: str) -> bool:
        return email in self.blocked_emails

fraud_engine = FraudDetectionEngine()
