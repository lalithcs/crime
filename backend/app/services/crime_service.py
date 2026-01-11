from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from typing import Optional, List
from math import radians, cos, sin, asin, sqrt

from app.models import crime, schemas


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km using Haversine formula"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r


def get_crimes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    crime_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = 5.0
) -> List[crime.Crime]:
    """Get crimes with filters"""
    query = db.query(crime.Crime)
    
    if crime_type:
        query = query.filter(crime.Crime.crime_type.ilike(f"%{crime_type}%"))
    
    if start_date:
        query = query.filter(crime.Crime.occurred_at >= start_date)
    
    if end_date:
        query = query.filter(crime.Crime.occurred_at <= end_date)
    
    crimes_list = query.order_by(crime.Crime.occurred_at.desc()).offset(skip).limit(limit).all()
    
    # Filter by location if provided
    if latitude is not None and longitude is not None:
        crimes_list = [
            c for c in crimes_list
            if haversine_distance(latitude, longitude, c.latitude, c.longitude) <= radius_km
        ]
    
    return crimes_list


def get_crime_stats(db: Session, days: int = 30) -> dict:
    """Get crime statistics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total_crimes = db.query(crime.Crime).filter(
        crime.Crime.occurred_at >= start_date
    ).count()
    
    by_type = db.query(
        crime.Crime.crime_type,
        func.count(crime.Crime.id).label("count")
    ).filter(
        crime.Crime.occurred_at >= start_date
    ).group_by(crime.Crime.crime_type).all()
    
    arrests = db.query(crime.Crime).filter(
        and_(
            crime.Crime.occurred_at >= start_date,
            crime.Crime.arrest_made == True
        )
    ).count()
    
    return {
        "total_crimes": total_crimes,
        "by_type": [{"type": t, "count": c} for t, c in by_type],
        "arrests": arrests,
        "arrest_rate": round(arrests / total_crimes * 100, 2) if total_crimes > 0 else 0,
        "period_days": days
    }


def get_heatmap_data(db: Session, crime_type: Optional[str], days: int = 30) -> dict:
    """Get crime heatmap data"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(
        crime.Crime.latitude,
        crime.Crime.longitude,
        crime.Crime.crime_type
    ).filter(crime.Crime.occurred_at >= start_date)
    
    if crime_type:
        query = query.filter(crime.Crime.crime_type.ilike(f"%{crime_type}%"))
    
    crimes_data = query.all()
    
    return {
        "points": [
            {"lat": c.latitude, "lng": c.longitude, "type": c.crime_type}
            for c in crimes_data
        ],
        "count": len(crimes_data)
    }


def create_crime_report(db: Session, report: schemas.ReportCreate) -> crime.CrimeReport:
    """Create a new crime report"""
    db_report = crime.CrimeReport(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_crime_reports(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> List[crime.CrimeReport]:
    """Get user-submitted crime reports"""
    query = db.query(crime.CrimeReport)
    
    if status:
        query = query.filter(crime.CrimeReport.status == status)
    
    return query.order_by(crime.CrimeReport.reported_at.desc()).offset(skip).limit(limit).all()
