from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.api import routes
from app.database import engine, Base
from app.services.websocket_manager import manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Crime Safety Platform API")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down Crime Safety Platform API")


app = FastAPI(
    title="Crime Prediction & Safety Platform API",
    description="Real-time crime prediction, reporting, and safety routing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://crime-lalithcs.vercel.app",
        "*"  # Allow all for now, restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.crimes_router, prefix="/api/crimes", tags=["Crimes"])
app.include_router(routes.reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(routes.predictions_router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(routes.routes_router, prefix="/api/routes", tags=["Safety Routes"])
app.include_router(routes.sentiment_router, prefix="/api/sentiment", tags=["Sentiment"])
app.include_router(routes.chatbot_router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(routes.alerts_router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(routes.causes_router, prefix="/api/causes", tags=["Causes"])
app.include_router(routes.websocket_router, prefix="/ws", tags=["WebSocket"])


@app.get("/")
async def root():
    return {
        "message": "Crime Prediction & Safety Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "crime-safety-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
