from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Import models to create tables
from app.database import Base, engine

# Create tables on startup
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 AgentNest API Starting...")
    yield
    # Shutdown
    print("🛑 AgentNest API Shutting down...")

app = FastAPI(
    title="AgentNest API",
    description="AI Agent Hosting Platform",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
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
        "version": "0.1.0"
    }

# Root Endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to AgentNest",
        "docs": "http://localhost:8000/docs",
        "api_version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
