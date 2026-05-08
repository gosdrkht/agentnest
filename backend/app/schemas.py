from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    is_active: bool
    balance: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Agent Schemas
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    docker_image: str
    cpu_limit: float = 1.0
    memory_limit_mb: int = 512

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cpu_limit: Optional[float] = None
    memory_limit_mb: Optional[int] = None

class Agent(AgentBase):
    id: int
    user_id: int
    status: str
    container_id: Optional[str] = None
    created_at: datetime
    last_run: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Usage Schemas
class UsageBase(BaseModel):
    cpu_hours: float
    memory_gb_hours: float
    uptime_hours: float
    cost: float

class Usage(UsageBase):
    id: int
    agent_id: int
    period_start: datetime
    period_end: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Billing Schemas
class BillingBase(BaseModel):
    amount: float
    status: str

class Billing(BillingBase):
    id: int
    user_id: int
    stripe_payment_id: Optional[str] = None
    invoice_number: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
