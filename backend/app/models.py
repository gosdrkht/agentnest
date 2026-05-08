from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    balance = Column(Numeric(10, 2), default=0)
    api_key = Column(String(255), unique=True, index=True)

    # Relationships
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    billing_records = relationship("Billing", back_populates="user", cascade="all, delete-orphan")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    docker_image = Column(String(255), nullable=False)
    status = Column(String(50), default="stopped")  # running, stopped, crashed, pending
    container_id = Column(String(255))
    cpu_limit = Column(Numeric(10, 2), default=1.0)
    memory_limit_mb = Column(Integer, default=512)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_run = Column(TIMESTAMP(timezone=True))
    logs = Column(Text)

    # Relationships
    owner = relationship("User", back_populates="agents")
    usage_records = relationship("Usage", back_populates="agent", cascade="all, delete-orphan")

class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    cpu_hours = Column(Numeric(10, 2))
    memory_gb_hours = Column(Numeric(10, 2))
    uptime_hours = Column(Numeric(10, 2))
    cost = Column(Numeric(10, 2))
    period_start = Column(TIMESTAMP(timezone=True))
    period_end = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    agent = relationship("Agent", back_populates="usage_records")

class Billing(Base):
    __tablename__ = "billing"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    stripe_payment_id = Column(String(255))
    invoice_number = Column(String(255))
    period_start = Column(TIMESTAMP(timezone=True))
    period_end = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    paid_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    user = relationship("User", back_populates="billing_records")
