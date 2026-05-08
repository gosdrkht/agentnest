"""
AgentNest Backend - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AgentNest API",
    description="AI Agent Hosting Platform - Deploy, Monitor, and Monetize AI Agents",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
]

if os.getenv("ENVIRONMENT") == "production":
    origins.extend([
        "https://agentnest.dev",
        "https://www.agentnest.dev",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ROUTES ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AgentNest API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "AgentNest API",
        "version": "0.1.0"
    }

@app.get("/api/v1/health")
async def api_health():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "AgentNest API",
        "version": "0.1.0"
    }

# ==================== ERROR HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if os.getenv("DEBUG") == "True" else "An error occurred"
        }
    )

# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    print("🚀 AgentNest API Starting...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Debug: {os.getenv('DEBUG', 'False')}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    print("🛑 AgentNest API Shutting down...")

# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG") == "True",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
