from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models to create tables
from app.database import Base, engine

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Import route handlers
from app.routes.auth import router as auth_router
from app.routes.agents import router as agents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 AgentNest API Starting...")
    logger.info("📦 Database tables created")
    logger.info("🐳 Docker service initialized")
    yield
    # Shutdown
    logger.info("🛑 AgentNest API Shutting down...")


app = FastAPI(
    title="AgentNest API",
    description="AI Agent Hosting Platform - Automated, Self-Managing Infrastructure",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "AgentNest API",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


# Root Endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to AgentNest - AI Agent Hosting Platform",
        "docs": "http://localhost:8000/docs",
        "api_version": "0.1.0",
        "endpoints": {
            "auth": "/api/auth",
            "agents": "/api/agents",
        }
    }


# Register routers
app.include_router(auth_router)
app.include_router(agents_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,
    )
