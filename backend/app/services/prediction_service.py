import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

from app.models import crime, schemas
from app.services.crime_service import haversine_distance


async def predict_crimes(db: Session, request: schemas.PredictionRequest) -> schemas.PredictionResponse:
    """
    Predict future crimes using ARIMA time-series model
    """
    # Get historical crime data
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)  # Use 1 year of data
    
    query = db.query(crime.Crime).filter(
        crime.Crime.occurred_at >= start_date
    )
    
    # Filter by crime type if specified
    if request.crime_type:
        query = query.filter(crime.Crime.crime_type.ilike(f"%{request.crime_type}%"))
    
    # Filter by location if specified
    crimes_data = query.all()
    if request.latitude and request.longitude:
        crimes_data = [
            c for c in crimes_data
            if haversine_distance(request.latitude, request.longitude, c.latitude, c.longitude) <= 5.0
        ]
    
    # Aggregate by day
    df = pd.DataFrame([
        {"date": c.occurred_at.date(), "count": 1}
        for c in crimes_data
    ])
    
    if df.empty or len(df) < 30:
        # Not enough data for ARIMA, return simple average
        return _simple_prediction(crimes_data, request.days_ahead)
    
    # Group by date and count
    daily_counts = df.groupby("date").count().reset_index()
    daily_counts.columns = ["date", "count"]
    daily_counts = daily_counts.set_index("date")
    daily_counts = daily_counts.asfreq('D', fill_value=0)
    
    # Fit ARIMA model
    try:
        # ARIMA(p, d, q) - using (1, 1, 1) as a good starting point
        model = ARIMA(daily_counts['count'], order=(1, 1, 1))
        fitted_model = model.fit()
        
        # Forecast
        forecast = fitted_model.forecast(steps=request.days_ahead)
        forecast_index = pd.date_range(
            start=daily_counts.index[-1] + timedelta(days=1),
            periods=request.days_ahead,
            freq='D'
        )
        
        # Confidence intervals
        forecast_df = fitted_model.get_forecast(steps=request.days_ahead)
        confidence_intervals = forecast_df.conf_int()
        
        # Calculate model accuracy on recent data
        recent_actual = daily_counts['count'].tail(30).values
        recent_pred = fitted_model.fittedvalues.tail(30).values
        mae = mean_absolute_error(recent_actual, recent_pred)
        accuracy = max(0, min(100, 100 - (mae / recent_actual.mean() * 100)))
        
        predictions = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "predicted_crimes": max(0, int(round(value))),
                "lower_bound": max(0, int(round(confidence_intervals.iloc[i, 0]))),
                "upper_bound": int(round(confidence_intervals.iloc[i, 1]))
            }
            for i, (date, value) in enumerate(zip(forecast_index, forecast))
        ]
        
        return schemas.PredictionResponse(
            predictions=predictions,
            confidence_interval={
                "lower": [p["lower_bound"] for p in predictions],
                "upper": [p["upper_bound"] for p in predictions]
            },
            accuracy=round(accuracy, 2),
            forecast_period=f"{request.days_ahead} days"
        )
    
    except Exception as e:
        print(f"ARIMA failed: {e}, falling back to simple prediction")
        return _simple_prediction(crimes_data, request.days_ahead)


def _simple_prediction(crimes_data: List, days_ahead: int) -> schemas.PredictionResponse:
    """Fallback simple prediction using moving average"""
    if not crimes_data:
        # No data, return zeros
        predictions = [
            {
                "date": (datetime.utcnow() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                "predicted_crimes": 0,
                "lower_bound": 0,
                "upper_bound": 0
            }
            for i in range(days_ahead)
        ]
        return schemas.PredictionResponse(
            predictions=predictions,
            confidence_interval={"lower": [0]*days_ahead, "upper": [0]*days_ahead},
            accuracy=0.0,
            forecast_period=f"{days_ahead} days"
        )
    
    # Calculate daily average from last 30 days
    recent_crimes = [c for c in crimes_data if c.occurred_at >= datetime.utcnow() - timedelta(days=30)]
    daily_avg = len(recent_crimes) / 30 if recent_crimes else len(crimes_data) / 365
    
    predictions = [
        {
            "date": (datetime.utcnow() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
            "predicted_crimes": max(0, int(round(daily_avg))),
            "lower_bound": max(0, int(round(daily_avg * 0.7))),
            "upper_bound": int(round(daily_avg * 1.3))
        }
        for i in range(days_ahead)
    ]
    
    return schemas.PredictionResponse(
        predictions=predictions,
        confidence_interval={
            "lower": [p["lower_bound"] for p in predictions],
            "upper": [p["upper_bound"] for p in predictions]
        },
        accuracy=50.0,
        forecast_period=f"{days_ahead} days (simple average)"
    )


async def get_hotspots(db: Session, days_ahead: int = 7) -> dict:
    """Get predicted crime hotspots using clustering"""
    from app.services.geocoding_service import get_area_name
    
    # Get recent crimes
    start_date = datetime.utcnow() - timedelta(days=90)
    crimes_data = db.query(crime.Crime).filter(
        crime.Crime.occurred_at >= start_date
    ).all()
    
    if not crimes_data:
        return {"hotspots": [], "message": "Insufficient data"}
    
    # Simple grid-based hotspot detection
    from collections import defaultdict
    grid_size = 0.01  # ~1km grid
    grid_counts = defaultdict(int)
    
    for c in crimes_data:
        grid_lat = round(c.latitude / grid_size) * grid_size
        grid_lng = round(c.longitude / grid_size) * grid_size
        grid_counts[(grid_lat, grid_lng)] += 1
    
    # Get top hotspots with area names
    sorted_grids = sorted(grid_counts.items(), key=lambda x: x[1], reverse=True)
    hotspots = [
        {
            "area": get_area_name(lat, lng),
            "latitude": lat,
            "longitude": lng,
            "crime_count": count,
            "predicted_increase": round(count * 0.1, 1),  # Simple 10% increase prediction
            "severity": "high" if count > 50 else "medium" if count > 20 else "low"
        }
        for (lat, lng), count in sorted_grids[:20]
    ]
    
    return {
        "hotspots": hotspots,
        "forecast_days": days_ahead,
        "analysis_period_days": 90
    }
