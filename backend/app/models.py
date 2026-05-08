"""
SQLAlchemy Database Models
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    balance = Column(Float, default=0.0)
    status = Column(String(20), default="active")  # active, suspended, deleted
    
    # Relationships
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    billing_records = relationship("Billing", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

class Agent(Base):
    """AI Agent model"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="stopped")  # running, stopped, crashed, deploying
    docker_image = Column(String(255), nullable=False)
    docker_container_id = Column(String(255))
    environment_variables = Column(JSON, default={})
    port = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_started = Column(DateTime)
    last_stopped = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="agents")
    logs = relationship("AgentLog", back_populates="agent", cascade="all, delete-orphan")
    usage_records = relationship("Usage", back_populates="agent", cascade="all, delete-orphan")

class AgentLog(Base):
    """Agent logs model"""
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    level = Column(String(20))  # INFO, ERROR, WARNING, DEBUG
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="logs")

class Usage(Base):
    """Usage tracking for billing"""
    __tablename__ = "usage"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    cpu_cores = Column(Float)
    memory_mb = Column(Float)
    storage_gb = Column(Float)
    uptime_hours = Column(Float)
    cost_amount = Column(Float)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="usage_records")

class Billing(Base):
    """Billing records"""
    __tablename__ = "billing"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20), default="pending")  # pending, paid, failed, cancelled
    stripe_payment_id = Column(String(255))
    stripe_invoice_id = Column(String(255))
    billing_period_start = Column(DateTime)
    billing_period_end = Column(DateTime)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="billing_records")

class Payment(Base):
    """Payment records"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50))  # stripe, paypal, crypto
    stripe_charge_id = Column(String(255))
    status = Column(String(20), default="processing")  # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payments")
