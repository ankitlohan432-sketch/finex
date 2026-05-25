"""
Database Models for Finex
All user data, transactions, loans, cards stored here
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, Text, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class LoanStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    REJECTED = "rejected"

class CardType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # User Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    
    # Financial Info
    balance = Column(Float, default=0.0)  # Available balance
    total_invested = Column(Float, default=0.0)  # Total invested in stocks
    portfolio_value = Column(Float, default=0.0)  # Current portfolio value
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

# Stock Holding Model
class StockHolding(Base):
    __tablename__ = "stock_holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    symbol = Column(String(255), index=True, nullable=False)
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    current_price = Column(Float, default=0.0)
    total_cost = Column(Float, nullable=False)  # quantity * average_price
    current_value = Column(Float, default=0.0)  # quantity * current_price
    gain_loss = Column(Float, default=0.0)  # current_value - total_cost
    gain_loss_percent = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Transaction Model
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    type = Column(Enum(TransactionType), nullable=False)  # buy, sell, deposit, etc
    symbol = Column(String(255), nullable=True)  # Stock symbol for buy/sell
    quantity = Column(Float, nullable=True)  # For buy/sell
    price = Column(Float, nullable=True)  # Price per unit
    amount = Column(Float, nullable=False)  # Total amount
    
    # Status
    status = Column(String(255), default="completed")  # completed, pending, failed
    description = Column(String(255), nullable=True)
    
    # Security
    is_fraud_flagged = Column(Boolean, default=False)
    fraud_reason = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Loan Model
class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Loan Details
    amount = Column(Float, nullable=False)  # Loan amount
    interest_rate = Column(Float, nullable=False)  # APR percentage (e.g., 5.0 for 5%)
    duration_months = Column(Integer, nullable=False)  # Loan duration
    monthly_payment = Column(Float, nullable=False)  # Monthly payment amount
    
    # Status
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    
    # Payment Info
    paid_amount = Column(Float, default=0.0)  # Total paid so far
    remaining_amount = Column(Float, nullable=False)  # Remaining to pay
    payments_completed = Column(Integer, default=0)  # Number of payments made
    
    # Dates
    start_date = Column(DateTime, nullable=True)  # When loan becomes active
    end_date = Column(DateTime, nullable=True)  # When loan completes
    next_payment_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Loan Payment Model
class LoanPayment(Base):
    __tablename__ = "loan_payments"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, index=True, nullable=False)
    
    amount = Column(Float, nullable=False)
    principal = Column(Float, nullable=False)  # Principal portion
    interest = Column(Float, nullable=False)  # Interest portion
    
    status = Column(String(255), default="completed")  # completed, pending, failed
    payment_method = Column(String(255), nullable=True)  # card, bank, etc
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Card Model
class PaymentCard(Base):
    __tablename__ = "payment_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Card Details
    card_holder_name = Column(String(255), nullable=False)
    card_number = Column(String(255), nullable=False)  # Last 4 digits for display
    card_type = Column(Enum(CardType), nullable=False)
    expiry_month = Column(Integer, nullable=False)
    expiry_year = Column(Integer, nullable=False)
    
    # Card Status
    is_primary = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Security
    is_fraud_flagged = Column(Boolean, default=False)
    fraud_reason = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Fraud Alert Model
class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Alert Details
    alert_type = Column(String(255), nullable=False)  # transaction, card, login
    severity = Column(String(255), nullable=False)  # low, medium, high, critical
    description = Column(Text, nullable=False)
    
    # Related Entity
    transaction_id = Column(Integer, nullable=True)
    card_id = Column(Integer, nullable=True)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Market Data Cache Model (for storing real-time stock data)
class MarketCache(Base):
    __tablename__ = "market_cache"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(255), index=True, unique=True, nullable=False)
    
    # Price Data
    current_price = Column(Float, nullable=False)
    open_price = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    
    # Change Data
    change = Column(Float, nullable=True)  # Absolute change
    change_percent = Column(Float, nullable=True)  # Percentage change
    
    # Volume
    volume = Column(Float, nullable=True)
    
    # Market Cap
    market_cap = Column(Float, nullable=True)
    
    # Update Time
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Analytics/Audit Log Model
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    
    # Action Details
    action = Column(String(255), nullable=False)  # login, buy, sell, loan_request, etc
    resource = Column(String(255), nullable=False)  # user, stock, loan, card
    resource_id = Column(Integer, nullable=True)
    
    # Details
    details = Column(JSON, nullable=True)
    ip_address = Column(String(255), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
