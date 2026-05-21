"""
Agent API Routes
Endpoints for deploying, managing, and monitoring AI agents
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Agent, User
from app.schemas import Agent as AgentSchema, AgentCreate, AgentUpdate
from app.utils.auth import get_current_user, TokenData
from app.services.docker_service import get_docker_service

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/", response_model=AgentSchema)
async def deploy_agent(
    agent_create: AgentCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deploy a new AI agent

    - **name**: Agent name
    - **description**: Agent description
    - **docker_image**: Docker image to run
    - **cpu_limit**: CPU cores (default: 1.0)
    - **memory_limit_mb**: Memory in MB (default: 512)
    """
    try:
        # Create database record
        db_agent = Agent(
            user_id=current_user.user_id,
            name=agent_create.name,
            description=agent_create.description,
            docker_image=agent_create.docker_image,
            cpu_limit=agent_create.cpu_limit,
            memory_limit_mb=agent_create.memory_limit_mb,
            status="deploying",
        )
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)

        # Deploy container
        docker_svc = get_docker_service()
        result = docker_svc.deploy_agent(
            agent_id=db_agent.id,
            user_id=current_user.user_id,
            docker_image=agent_create.docker_image,
            name=agent_create.name,
            cpu_limit=agent_create.cpu_limit,
            memory_limit_mb=agent_create.memory_limit_mb,
        )

        # Update agent with container info
        db_agent.container_id = result["container_id"]
        db_agent.status = "running"
        db_agent.last_started = datetime.utcnow()
        db.commit()
        db.refresh(db_agent)

        return db_agent

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to deploy agent: {str(e)}")


@router.get("/", response_model=List[AgentSchema])
async def list_agents(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all agents for current user"""
    agents = db.query(Agent).filter(Agent.user_id == current_user.user_id).all()
    return agents


@router.get("/{agent_id}", response_model=AgentSchema)
async def get_agent(
    agent_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get agent details"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.user_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent


@router.put("/{agent_id}", response_model=AgentSchema)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update agent configuration"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.user_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)
    return agent


@router.post("/{agent_id}/start")
async def start_agent(
    agent_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a stopped agent"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.user_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    docker_svc = get_docker_service()
    success = docker_svc.start_agent(agent_id, current_user.user_id)

    if success:
        agent.status = "running"
        agent.last_started = datetime.utcnow()
        db.commit()
        return {"status": "started", "agent_id": agent_id}
    else:
        raise HTTPException(status_code=400, detail="Failed to start agent")


@router.post("/{agent_id}/stop")
async def stop_agent(
    agent_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stop a running agent"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.user_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    docker_svc = get_docker_service()
    success = docker_svc.stop_agent(agent_id, current_user.user_id)

    if success:
        agent.status = "stopped"
        agent.last_stopped = datetime.utcnow()
        db.commit()
        return {"status": "stopped", "agent_id": agent_id}
    else:
        raise HTTPException(status_code=400, detail="Failed to stop agent")


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an agent"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.user_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    docker_svc = get_docker_service()
    docker_svc.delete_agent(agent_id, current_user.user_id)

    db.delete(agent)
    db.commit()

    return {"status": "deleted", "agent_id": agent_id}


@router.get("/{agent_id}/logs")
async def get_agent_logs(
    agent_id: int,
    tail: int = 100,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get agent logs"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.user_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    docker_svc = get_docker_service()
    logs = docker_svc.get_agent_logs(agent_id, current_user.user_id, tail=tail)

    return {
        "agent_id": agent_id,
        "logs": logs.split("\n") if logs else [],
        "timestamp": datetime.utcnow(),
    }


@router.get("/{agent_id}/stats")
async def get_agent_stats(
    agent_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get real-time resource usage statistics"""
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.user_id == current_user.user_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    docker_svc = get_docker_service()
    stats = docker_svc.get_agent_stats(agent_id, current_user.user_id)

    return {
        "agent_id": agent_id,
        "stats": stats,
        "timestamp": datetime.utcnow(),
    }
