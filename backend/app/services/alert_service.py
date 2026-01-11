from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.models import crime
from app.services.crime_service import haversine_distance


def get_alerts(
    db: Session,
    active_only: bool = True,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = 10.0
) -> List[crime.Alert]:
    """Get community alerts"""
    query = db.query(crime.Alert)
    
    if active_only:
        query = query.filter(crime.Alert.active == True)
        query = query.filter(
            (crime.Alert.expires_at.is_(None)) | 
            (crime.Alert.expires_at > datetime.utcnow())
        )
    
    alerts = query.order_by(crime.Alert.created_at.desc()).all()
    
    # Filter by location if provided
    if latitude is not None and longitude is not None:
        filtered_alerts = []
        for alert in alerts:
            if alert.latitude is None or alert.longitude is None:
                # Global alerts
                filtered_alerts.append(alert)
            elif haversine_distance(latitude, longitude, alert.latitude, alert.longitude) <= alert.radius_km:
                filtered_alerts.append(alert)
        return filtered_alerts
    
    return alerts


def create_alert(
    db: Session,
    title: str,
    message: str,
    alert_type: str,
    severity: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 1.0,
    expires_in_hours: Optional[int] = None
) -> crime.Alert:
    """Create a new community alert"""
    expires_at = None
    if expires_in_hours:
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    alert = crime.Alert(
        title=title,
        message=message,
        alert_type=alert_type,
        severity=severity,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        expires_at=expires_at
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return alert


def deactivate_alert(db: Session, alert_id: int) -> bool:
    """Deactivate an alert"""
    alert = db.query(crime.Alert).filter(crime.Alert.id == alert_id).first()
    if alert:
        alert.active = False
        db.commit()
        return True
    return False


def check_and_create_auto_alerts(db: Session):
    """
    Automatically create alerts based on crime patterns
    Called periodically to detect crime spikes
    """
    from datetime import timedelta
    from collections import defaultdict
    
    # Get crimes from last 24 hours
    recent_crimes = db.query(crime.Crime).filter(
        crime.Crime.occurred_at >= datetime.utcnow() - timedelta(hours=24)
    ).all()
    
    # Group by grid cell
    grid_size = 0.01  # ~1km
    grid_crimes = defaultdict(list)
    
    for c in recent_crimes:
        grid_lat = round(c.latitude / grid_size) * grid_size
        grid_lng = round(c.longitude / grid_size) * grid_size
        grid_crimes[(grid_lat, grid_lng)].append(c)
    
    # Check for spikes (>10 crimes in 24h in 1km area)
    for (lat, lng), crimes_list in grid_crimes.items():
        if len(crimes_list) >= 10:
            # Check if alert already exists
            existing = db.query(crime.Alert).filter(
                crime.Alert.latitude == lat,
                crime.Alert.longitude == lng,
                crime.Alert.active == True,
                crime.Alert.alert_type == "crime_spike"
            ).first()
            
            if not existing:
                create_alert(
                    db,
                    title="Crime Spike Alert",
                    message=f"High crime activity detected in this area: {len(crimes_list)} incidents in 24 hours",
                    alert_type="crime_spike",
                    severity="high",
                    latitude=lat,
                    longitude=lng,
                    radius_km=1.0,
                    expires_in_hours=48
                )
