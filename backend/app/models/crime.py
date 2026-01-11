from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class Crime(Base):
    """Crime incident model"""
    __tablename__ = "crimes"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(50), unique=True, index=True)
    crime_type = Column(String(100), index=True)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_description = Column(String(200))
    occurred_at = Column(DateTime, nullable=False, index=True)
    reported_at = Column(DateTime, default=func.now())
    arrest_made = Column(Boolean, default=False)
    domestic = Column(Boolean, default=False)
    district = Column(String(20))
    ward = Column(Integer)
    
    # User-reported flag
    user_reported = Column(Boolean, default=False)
    reported_by_user_id = Column(String(100), nullable=True)
    
    # Predictions
    is_predicted = Column(Boolean, default=False)
    prediction_confidence = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CrimeReport(Base):
    """User-submitted crime reports"""
    __tablename__ = "crime_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    crime_type = Column(String(100))
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_description = Column(String(200))
    photo_url = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")  # pending, verified, rejected
    reported_at = Column(DateTime, default=func.now())
    verified_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=func.now())


class Alert(Base):
    """Community alerts"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    message = Column(Text)
    alert_type = Column(String(50))  # crime_spike, prediction, safety_warning
    severity = Column(String(20))  # low, medium, high, critical
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_km = Column(Float, default=1.0)
    active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=func.now())


class EnvironmentalFactor(Base):
    """Environmental factors affecting crime (lighting, construction, etc.)"""
    __tablename__ = "environmental_factors"

    id = Column(Integer, primary_key=True, index=True)
    factor_type = Column(String(50))  # poor_lighting, construction, abandoned_building
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(String(20))  # low, medium, high
    reported_at = Column(DateTime, default=func.now())
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=func.now())


class Sentiment(Base):
    """Citizen sentiment analysis"""
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    sentiment = Column(String(20))  # positive, negative, neutral
    sentiment_score = Column(Float)
    location = Column(String(200))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source = Column(String(50))  # user_report, social_media, survey
    
    created_at = Column(DateTime, default=func.now())
