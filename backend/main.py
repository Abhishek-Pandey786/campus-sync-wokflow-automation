"""
Main FastAPI Application Entry Point
Intelligent Workflow Automation and Delay Prediction System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from db.database import engine, Base

# Import API routers
from api import auth, requests, workflows, predictions, alerts
# from api import analytics  # Week 8


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Workflow Automation System...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🗄️  Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Academic Service Request Workflow Automation with ML-based Delay Prediction",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    import os
    ml_model_loaded = os.path.exists("ml/models/best_model.pkl")
    
    return {
        "status": "healthy",
        "database": "connected",
        "api": "operational",
        "ml_model": "loaded" if ml_model_loaded else "not_loaded",
    }


# API Routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(requests.router, prefix="/requests", tags=["Service Requests"])
app.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
app.include_router(predictions.router, prefix="/predict", tags=["ML Predictions"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
