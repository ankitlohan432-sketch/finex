from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from database import Base
from datetime import datetime

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    page = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    extra_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Analytics {self.user_id} {self.action}>"
