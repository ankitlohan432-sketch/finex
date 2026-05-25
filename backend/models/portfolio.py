from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    total_balance = Column(Float, default=0.0)
    invested_amount = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    profit_loss_percentage = Column(Float, default=0.0)
    
    cash_available = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="portfolio")
    
    def __repr__(self):
        return f"<Portfolio user_id={self.user_id} balance={self.total_balance}>"
