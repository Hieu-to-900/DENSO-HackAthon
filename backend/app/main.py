"""FastAPI application main file."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.action_routes import router as action_router
from app.api.alert_routes import router as alert_router
from app.api.forecast_routes import router as forecast_router
from app.api.job_routes import router as job_router
from app.api.routes import router
from app.database.connection import close_db, init_db
from app.api.notification_routes import router as notification_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("🚀 Starting DENSO Forecast API...")
    await init_db()
    yield
    # Shutdown
    print("🛑 Shutting down DENSO Forecast API...")
    await close_db()


app = FastAPI(
    title="AI Demand Forecasting API",
    description="API for demand forecasting dashboard with alert system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["api"])
app.include_router(alert_router, prefix="/api", tags=["alerts"])
app.include_router(forecast_router, prefix="/api", tags=["forecasts"])
app.include_router(job_router, prefix="/api", tags=["jobs"])
app.include_router(action_router, tags=["actions"])  # Already has /api/actions prefix


app.include_router(notification_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Demand Forecasting API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

