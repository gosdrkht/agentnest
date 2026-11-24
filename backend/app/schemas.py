from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    is_active: bool
    balance: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Agent Schemas
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    docker_image: str = Field(..., min_length=1, max_length=255)
    cpu_limit: float = Field(default=1.0, gt=0, le=16.0)
    memory_limit_mb: int = Field(default=512, ge=64, le=32768)

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    cpu_limit: Optional[float] = Field(default=None, gt=0, le=16.0)
    memory_limit_mb: Optional[int] = Field(default=None, ge=64, le=32768)

class Agent(AgentBase):
    id: int
    user_id: int
    status: str
    container_id: Optional[str] = None
    created_at: datetime
    last_run: Optional[datetime] = None
    last_started: Optional[datetime] = None
    last_stopped: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
