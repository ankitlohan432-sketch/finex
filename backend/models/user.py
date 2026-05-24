from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    TRADER = "trader"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)

    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    role = Column(Enum(UserRole), default=UserRole.USER)

    # OTP fields
    otp_code = Column(String(10), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    otp_attempts = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relations
    portfolio = relationship("Portfolio", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"

class VisitorLog(Base):
    __tablename__ = "visitor_logs"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(50), nullable=False)
    user_agent = Column(String(500), nullable=False)
    page = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Visitor {self.ip_address} at {self.created_at}>"
