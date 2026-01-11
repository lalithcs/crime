from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CrimeBase(BaseModel):
    crime_type: str
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_description: Optional[str] = None


class CrimeCreate(CrimeBase):
    case_id: str
    occurred_at: datetime
    arrest_made: bool = False
    domestic: bool = False
    district: Optional[str] = None
    ward: Optional[int] = None


class CrimeResponse(CrimeBase):
    id: int
    case_id: str
    occurred_at: datetime
    reported_at: datetime
    user_reported: bool
    is_predicted: bool
    prediction_confidence: Optional[float] = None
    
    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    user_id: str
    crime_type: str
    description: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_description: Optional[str] = None
    photo_url: Optional[str] = None


class ReportResponse(BaseModel):
    id: int
    user_id: str
    crime_type: str
    description: str
    latitude: float
    longitude: float
    location_description: Optional[str]
    status: str
    reported_at: datetime
    
    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    days_ahead: int = Field(7, ge=1, le=30)
    crime_type: Optional[str] = None


class PredictionResponse(BaseModel):
    predictions: List[dict]
    confidence_interval: dict
    accuracy: float
    forecast_period: str
    
    model_config = {"protected_namespaces": ()}


class SafeRouteRequest(BaseModel):
    start_lat: float = Field(..., ge=-90, le=90)
    start_lng: float = Field(..., ge=-180, le=180)
    end_lat: float = Field(..., ge=-90, le=90)
    end_lng: float = Field(..., ge=-180, le=180)
    avoid_crime_radius_km: float = Field(0.5, ge=0.1, le=5.0)
    time_of_day: Optional[str] = None  # morning, afternoon, evening, night


class SafeRouteResponse(BaseModel):
    route: List[List[float]]  # [[lat, lng], [lat, lng], ...]
    distance_km: float
    duration_minutes: float
    safety_score: float
    avoided_crime_zones: int
    waypoints: List[dict]


class SentimentRequest(BaseModel):
    text: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SentimentResponse(BaseModel):
    sentiment: str  # positive, negative, neutral
    sentiment_score: float
    confidence: float
    text: str


class ChatbotRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    context: Optional[dict] = None


class ChatbotResponse(BaseModel):
    response: str
    intent: str
    data: Optional[dict] = None


class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    alert_type: str
    severity: str
    latitude: Optional[float]
    longitude: Optional[float]
    radius_km: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class EnvironmentalFactorResponse(BaseModel):
    id: int
    factor_type: str
    description: str
    latitude: float
    longitude: float
    severity: str
    reported_at: datetime
    resolved: bool
    
    class Config:
        from_attributes = True
