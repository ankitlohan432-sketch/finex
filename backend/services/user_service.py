"""
User Service
Handles user profile, account management, and KYC
"""

from datetime import datetime
from typing import Optional

class UserService:
    """Service for managing users and accounts"""
    
    def __init__(self):
        self.users_db = {}  # In-memory storage (use real DB in production)
    
    async def create_user(self, email: str, full_name: str, password_hash: str, 
                         phone: Optional[str] = None):
        """Create a new user"""
        
        user = {
            "id": len(self.users_db) + 1,
            "email": email,
            "full_name": full_name,
            "phone": phone,
            "password_hash": password_hash,
            "is_active": True,
            "is_verified": False,
            "is_admin": False,
            "role": "user",
            "balance": 10000.0,  # Starting balance
            "total_invested": 0.0,
            "portfolio_value": 0.0,
            "kyc_status": "pending",
            "kyc_verified_at": None,
            "account_created_at": datetime.utcnow().isoformat(),
            "last_login": None
        }
        
        self.users_db[email] = user
        return user
    
    async def get_user(self, email: str):
        """Get user by email"""
        return self.users_db.get(email)
    
    async def get_user_by_id(self, user_id: int):
        """Get user by ID"""
        for user in self.users_db.values():
            if user["id"] == user_id:
                return user
        return None
    
    async def update_balance(self, user_id: int, amount: float):
        """Update user balance"""
        for user in self.users_db.values():
            if user["id"] == user_id:
                user["balance"] += amount
                user["updated_at"] = datetime.utcnow().isoformat()
                return user
        return None
    
    async def update_profile(self, user_id: int, updates: dict):
        """Update user profile"""
        for user in self.users_db.values():
            if user["id"] == user_id:
                # Only allow certain fields to be updated
                allowed_fields = ["full_name", "phone"]
                for field in allowed_fields:
                    if field in updates:
                        user[field] = updates[field]
                user["updated_at"] = datetime.utcnow().isoformat()
                return user
        return None
    
    async def verify_email(self, email: str):
        """Mark email as verified"""
        if email in self.users_db:
            self.users_db[email]["is_verified"] = True
            self.users_db[email]["email_verified_at"] = datetime.utcnow().isoformat()
            return self.users_db[email]
        return None
    
    async def update_last_login(self, user_id: int):
        """Update last login timestamp"""
        for user in self.users_db.values():
            if user["id"] == user_id:
                user["last_login"] = datetime.utcnow().isoformat()
                return user
        return None
    
    async def verify_kyc(self, user_id: int, kyc_data: dict):
        """Verify KYC (Know Your Customer) information"""
        for user in self.users_db.values():
            if user["id"] == user_id:
                user["kyc_status"] = "verified"
                user["kyc_verified_at"] = datetime.utcnow().isoformat()
                user["kyc_data"] = kyc_data
                return user
        return None
    
    async def get_user_stats(self, user_id: int):
        """Get user statistics and analytics"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        return {
            "user_id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "account_age_days": self._calculate_days_since(user["account_created_at"]),
            "balance": user["balance"],
            "total_invested": user.get("total_invested", 0),
            "portfolio_value": user.get("portfolio_value", 0),
            "kyc_status": user.get("kyc_status", "pending"),
            "is_verified": user["is_verified"],
            "last_login": user.get("last_login"),
            "account_created_at": user["account_created_at"]
        }
    
    async def get_all_users_stats(self):
        """Get statistics for all users (admin only)"""
        users = list(self.users_db.values())
        
        return {
            "total_users": len(users),
            "verified_users": sum(1 for u in users if u["is_verified"]),
            "active_users": sum(1 for u in users if u["is_active"]),
            "kyc_verified_users": sum(1 for u in users if u.get("kyc_status") == "verified"),
            "total_balance": sum(u["balance"] for u in users),
            "total_invested": sum(u.get("total_invested", 0) for u in users),
            "users": [
                {
                    "id": u["id"],
                    "email": u["email"],
                    "name": u["full_name"],
                    "balance": u["balance"],
                    "invested": u.get("total_invested", 0),
                    "kyc_status": u.get("kyc_status", "pending"),
                    "created_at": u["account_created_at"]
                }
                for u in users
            ]
        }
    
    async def disable_account(self, user_id: int):
        """Disable a user account"""
        for user in self.users_db.values():
            if user["id"] == user_id:
                user["is_active"] = False
                user["disabled_at"] = datetime.utcnow().isoformat()
                return user
        return None
    
    async def enable_account(self, user_id: int):
        """Enable a disabled account"""
        for user in self.users_db.values():
            if user["id"] == user_id:
                user["is_active"] = True
                user["disabled_at"] = None
                return user
        return None
    
    @staticmethod
    def _calculate_days_since(iso_date: str) -> int:
        """Calculate days since ISO date string"""
        try:
            date = datetime.fromisoformat(iso_date)
            return (datetime.utcnow() - date).days
        except:
            return 0

# Export service
user_service = UserService()
