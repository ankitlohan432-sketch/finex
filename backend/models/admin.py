from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean
from database import Base
from datetime import datetime

class AdminSettings(Base):
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(255), unique=True, nullable=False)
    setting_value = Column(String(255), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AdminSettings {self.setting_key}>"

class PlatformStats(Base):
    __tablename__ = "platform_stats"

    id = Column(Integer, primary_key=True, index=True)
    
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    total_transactions = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)
    
    fraud_attempts = Column(Integer, default=0)
    fraud_blocked = Column(Integer, default=0)
    
    daily_signups = Column(Integer, default=0)
    
    api_uptime = Column(Float, default=99.99)
    avg_response_time = Column(Float, default=0.0)
    
    extra_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PlatformStats users={self.total_users}>"
