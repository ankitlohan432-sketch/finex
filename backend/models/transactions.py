from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    DIVIDEND = "dividend"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    symbol = Column(String(255), nullable=True)  # Stock symbol if applicable
    quantity = Column(Float, default=0)
    price_per_unit = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    
    description = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.type} {self.total_amount}>"
