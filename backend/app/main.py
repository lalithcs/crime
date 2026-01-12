from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.api import routes
from app.database import engine, Base, SessionLocal
from app.services.websocket_manager import manager
from app.models import crime as crime_model
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def auto_load_data_if_empty():
    """Auto-load sample data if database is empty"""
    db = SessionLocal()
    try:
        # Check if database has any crimes
        crime_count = db.query(crime_model.Crime).count()
        
        if crime_count == 0:
            logger.info("Database is empty. Auto-loading sample data...")
            
            from scripts.ingest_data import generate_synthetic_data
            
            count = 0
            for record in generate_synthetic_data(1000):
                try:
                    crime_obj = crime_model.Crime(
                        case_id=record["id"],
                        crime_type=record["primary_type"],
                        description=record.get("description", ""),
                        latitude=record["latitude"],
                        longitude=record["longitude"],
                        location_description=record.get("location_description", ""),
                        occurred_at=record["date"] if isinstance(record["date"], datetime) else datetime.fromisoformat(record["date"].replace("Z", "+00:00")),
                        arrest_made=record.get("arrest", False),
                        domestic=record.get("domestic", False),
                        district=record.get("district", ""),
                        ward=record.get("ward"),
                    )
                    db.add(crime_obj)
                    count += 1
                    
                    # Commit in batches
                    if count % 100 == 0:
                        db.commit()
                        logger.info(f"Loaded {count} records...")
                        
                except Exception as e:
                    logger.error(f"Error adding record: {e}")
                    continue
            
            db.commit()
            logger.info(f"✅ Auto-loaded {count} crime records successfully!")
        else:
            logger.info(f"Database already has {crime_count} records. Skipping auto-load.")
            
    except Exception as e:
        logger.error(f"Error during auto-load: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events"""
    # Startup
    logger.info("Starting CrimeScope API")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    # Auto-load data if database is empty
    auto_load_data_if_empty()
    
    yield
    # Shutdown
    logger.info("Shutting down CrimeScope API")


app = FastAPI(
    title="CrimeScope API",
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
