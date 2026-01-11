from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.models import crime
from app.services.crime_service import haversine_distance


def get_environmental_factors(
    db: Session,
    factor_type: Optional[str] = None,
    resolved: Optional[bool] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = 5.0
) -> List[crime.EnvironmentalFactor]:
    """Get environmental factors (lighting, construction, etc.)"""
    query = db.query(crime.EnvironmentalFactor)
    
    if factor_type:
        query = query.filter(crime.EnvironmentalFactor.factor_type == factor_type)
    
    if resolved is not None:
        query = query.filter(crime.EnvironmentalFactor.resolved == resolved)
    
    factors = query.order_by(crime.EnvironmentalFactor.reported_at.desc()).all()
    
    # Filter by location if provided
    if latitude is not None and longitude is not None:
        factors = [
            f for f in factors
            if haversine_distance(latitude, longitude, f.latitude, f.longitude) <= radius_km
        ]
    
    return factors


def create_environmental_factor(
    db: Session,
    factor_type: str,
    description: str,
    latitude: float,
    longitude: float,
    severity: str = "medium"
) -> crime.EnvironmentalFactor:
    """Report a new environmental factor"""
    factor = crime.EnvironmentalFactor(
        factor_type=factor_type,
        description=description,
        latitude=latitude,
        longitude=longitude,
        severity=severity
    )
    
    db.add(factor)
    db.commit()
    db.refresh(factor)
    
    return factor


def resolve_environmental_factor(db: Session, factor_id: int) -> bool:
    """Mark an environmental factor as resolved"""
    factor = db.query(crime.EnvironmentalFactor).filter(
        crime.EnvironmentalFactor.id == factor_id
    ).first()
    
    if factor:
        factor.resolved = True
        factor.resolved_at = datetime.utcnow()
        db.commit()
        return True
    
    return False


def analyze_environmental_correlation(db: Session) -> dict:
    """
    Analyze correlation between environmental factors and crimes
    Returns insights about how factors affect crime rates
    """
    from datetime import timedelta
    
    # Get all unresolved environmental factors
    factors = db.query(crime.EnvironmentalFactor).filter(
        crime.EnvironmentalFactor.resolved == False
    ).all()
    
    # Get crimes from last 90 days
    recent_crimes = db.query(crime.Crime).filter(
        crime.Crime.occurred_at >= datetime.utcnow() - timedelta(days=90)
    ).all()
    
    # Count crimes near each factor type
    factor_crime_counts = {}
    
    for factor_type in ["poor_lighting", "construction", "abandoned_building"]:
        type_factors = [f for f in factors if f.factor_type == factor_type]
        nearby_crimes = 0
        
        for factor in type_factors:
            for c in recent_crimes:
                if haversine_distance(factor.latitude, factor.longitude, c.latitude, c.longitude) <= 0.5:
                    nearby_crimes += 1
        
        factor_crime_counts[factor_type] = {
            "factor_count": len(type_factors),
            "nearby_crimes": nearby_crimes,
            "crimes_per_factor": round(nearby_crimes / len(type_factors), 2) if type_factors else 0
        }
    
    return {
        "analysis": factor_crime_counts,
        "total_factors": len(factors),
        "total_recent_crimes": len(recent_crimes),
        "recommendation": _generate_factor_recommendations(factor_crime_counts)
    }


def _generate_factor_recommendations(factor_stats: dict) -> List[str]:
    """Generate recommendations based on environmental factor analysis"""
    recommendations = []
    
    for factor_type, stats in factor_stats.items():
        if stats["crimes_per_factor"] > 5:
            if factor_type == "poor_lighting":
                recommendations.append(
                    f"High crime near poorly lit areas ({stats['crimes_per_factor']:.1f} crimes/location). "
                    "Recommend installing additional street lighting."
                )
            elif factor_type == "construction":
                recommendations.append(
                    f"Elevated crime near construction sites ({stats['crimes_per_factor']:.1f} crimes/location). "
                    "Recommend increased police patrols and better site security."
                )
            elif factor_type == "abandoned_building":
                recommendations.append(
                    f"High crime near abandoned buildings ({stats['crimes_per_factor']:.1f} crimes/location). "
                    "Recommend property redevelopment or increased monitoring."
                )
    
    if not recommendations:
        recommendations.append("No significant environmental correlations detected. Continue monitoring.")
    
    return recommendations
