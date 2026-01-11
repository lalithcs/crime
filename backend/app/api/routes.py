from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import crime, schemas
from app.services import crime_service, prediction_service, route_service
from app.services import sentiment_service, chatbot_service, alert_service, cause_service
from app.services.websocket_manager import manager

# Initialize routers
crimes_router = APIRouter()
reports_router = APIRouter()
predictions_router = APIRouter()
routes_router = APIRouter()
sentiment_router = APIRouter()
chatbot_router = APIRouter()
alerts_router = APIRouter()
causes_router = APIRouter()
websocket_router = APIRouter()


# ==================== CRIMES ====================
@crimes_router.get("/", response_model=List[schemas.CrimeResponse])
async def get_crimes(
    skip: int = 0,
    limit: int = 100,
    crime_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = 5.0,
    db: Session = Depends(get_db)
):
    """Get crimes with optional filters"""
    crimes = crime_service.get_crimes(
        db, skip=skip, limit=limit, crime_type=crime_type,
        start_date=start_date, end_date=end_date,
        latitude=latitude, longitude=longitude, radius_km=radius_km
    )
    return crimes


@crimes_router.get("/stats")
async def get_crime_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get crime statistics for the last N days"""
    stats = crime_service.get_crime_stats(db, days)
    return stats


@crimes_router.get("/heatmap")
async def get_crime_heatmap(
    crime_type: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get crime heatmap data"""
    heatmap = crime_service.get_heatmap_data(db, crime_type, days)
    return heatmap


# ==================== REPORTS ====================
@reports_router.post("/", response_model=schemas.ReportResponse)
async def create_report(
    report: schemas.ReportCreate,
    db: Session = Depends(get_db)
):
    """Submit a new crime report"""
    new_report = crime_service.create_crime_report(db, report)
    
    # Broadcast to all connected WebSocket clients
    await manager.broadcast({
        "type": "new_report",
        "data": {
            "id": new_report.id,
            "crime_type": new_report.crime_type,
            "latitude": new_report.latitude,
            "longitude": new_report.longitude,
            "reported_at": new_report.reported_at.isoformat()
        }
    })
    
    return new_report


@reports_router.get("/", response_model=List[schemas.ReportResponse])
async def get_reports(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get user-submitted crime reports"""
    reports = crime_service.get_crime_reports(db, skip, limit, status)
    return reports


# ==================== PREDICTIONS ====================
@predictions_router.post("/", response_model=schemas.PredictionResponse)
async def predict_crimes(
    request: schemas.PredictionRequest,
    db: Session = Depends(get_db)
):
    """Get crime predictions using ARIMA model"""
    try:
        predictions = await prediction_service.predict_crimes(db, request)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@predictions_router.get("/hotspots")
async def get_predicted_hotspots(
    days_ahead: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get predicted crime hotspots"""
    hotspots = await prediction_service.get_hotspots(db, days_ahead)
    return hotspots


# ==================== SAFE ROUTES ====================
@routes_router.post("/safe", response_model=schemas.SafeRouteResponse)
async def get_safe_route(
    request: schemas.SafeRouteRequest,
    db: Session = Depends(get_db)
):
    """Calculate the safest route avoiding crime zones"""
    try:
        route = await route_service.calculate_safe_route(db, request)
        return route
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route calculation failed: {str(e)}")


@routes_router.post("/compare")
async def compare_routes(
    request: schemas.SafeRouteRequest,
    db: Session = Depends(get_db)
):
    """Compare safe route vs fastest route"""
    comparison = await route_service.compare_routes(db, request)
    return comparison


# ==================== SENTIMENT ====================
@sentiment_router.post("/", response_model=schemas.SentimentResponse)
async def analyze_sentiment(
    request: schemas.SentimentRequest,
    db: Session = Depends(get_db)
):
    """Analyze sentiment of citizen text"""
    result = await sentiment_service.analyze_sentiment(db, request)
    return result


@sentiment_router.get("/trends")
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=365),
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get sentiment trends over time"""
    trends = sentiment_service.get_sentiment_trends(db, days, location)
    return trends


# ==================== CHATBOT ====================
@chatbot_router.post("/", response_model=schemas.ChatbotResponse)
async def chat(
    request: schemas.ChatbotRequest,
    db: Session = Depends(get_db)
):
    """Chat with crime information bot"""
    response = await chatbot_service.process_message(db, request)
    return response


# ==================== ALERTS ====================
@alerts_router.get("/", response_model=List[schemas.AlertResponse])
async def get_alerts(
    active_only: bool = True,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = 10.0,
    db: Session = Depends(get_db)
):
    """Get community alerts"""
    alerts = alert_service.get_alerts(
        db, active_only, latitude, longitude, radius_km
    )
    return alerts


@alerts_router.post("/")
async def create_alert(
    title: str,
    message: str,
    alert_type: str,
    severity: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 1.0,
    db: Session = Depends(get_db)
):
    """Create a new community alert"""
    alert = alert_service.create_alert(
        db, title, message, alert_type, severity,
        latitude, longitude, radius_km
    )
    
    # Broadcast alert
    await manager.broadcast({
        "type": "new_alert",
        "data": {
            "id": alert.id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity,
            "latitude": alert.latitude,
            "longitude": alert.longitude
        }
    })
    
    return alert


# ==================== CAUSES ====================
@causes_router.get("/", response_model=List[schemas.EnvironmentalFactorResponse])
async def get_environmental_factors(
    factor_type: Optional[str] = None,
    resolved: Optional[bool] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = 5.0,
    db: Session = Depends(get_db)
):
    """Get environmental factors affecting crime"""
    factors = cause_service.get_environmental_factors(
        db, factor_type, resolved, latitude, longitude, radius_km
    )
    return factors


@causes_router.post("/")
async def report_environmental_factor(
    factor_type: str,
    description: str,
    latitude: float,
    longitude: float,
    severity: str = "medium",
    db: Session = Depends(get_db)
):
    """Report an environmental factor"""
    factor = cause_service.create_environmental_factor(
        db, factor_type, description, latitude, longitude, severity
    )
    return factor


# ==================== WEBSOCKET ====================
@websocket_router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            # Echo back or process as needed
            await websocket.send_json({"type": "pong", "data": "Connection alive"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ==================== ADMIN / SETUP ====================
@crimes_router.get("/setup/load-data")
async def load_sample_data(db: Session = Depends(get_db)):
    """Load sample crime data for demo/testing"""
    try:
        import sys
        import os
        # Add backend directory to path
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, backend_path)
        
        from scripts.ingest_data import generate_synthetic_data
        
        # Generate data directly in the database
        count = 0
        for record in generate_synthetic_data(1000):
            try:
                crime_obj = crime.Crime(
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
            except Exception as e:
                print(f"Error adding record: {e}")
                continue
        
        db.commit()
        return {"status": "success", "message": f"Loaded {count} crime records"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")
