from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import re

from app.models import crime, schemas
from app.services import crime_service, prediction_service


async def process_message(db: Session, request: schemas.ChatbotRequest) -> schemas.ChatbotResponse:
    """
    Process chatbot message and generate response
    Simple rule-based chatbot for crime information queries
    """
    message = request.message.lower().strip()
    
    # Intent detection
    intent = _detect_intent(message)
    
    # Process based on intent
    if intent == "crime_stats":
        data = await _handle_crime_stats(db, message)
        response = _format_crime_stats_response(data)
        
    elif intent == "prediction":
        data = await _handle_prediction_query(db, message)
        response = _format_prediction_response(data)
        
    elif intent == "safety_tips":
        response = _get_safety_tips()
        data = None
        
    elif intent == "report_crime":
        response = _get_report_instructions()
        data = {"action": "redirect_to_report_form"}
        
    elif intent == "emergency":
        response = _get_emergency_info()
        data = {"emergency_numbers": {"police": "911", "ambulance": "911", "fire": "911"}}
        
    elif intent == "location_safety":
        data = await _handle_location_safety(db, message)
        response = _format_location_safety_response(data)
        
    else:
        response = _get_default_response()
        data = {"suggestions": [
            "Ask about crime statistics",
            "Request crime predictions",
            "Get safety tips",
            "Report a crime"
        ]}
    
    return schemas.ChatbotResponse(
        response=response,
        intent=intent,
        data=data
    )


def _detect_intent(message: str) -> str:
    """Detect user intent from message"""
    # Keywords for intent classification
    intents = {
        "crime_stats": ["statistics", "stats", "how many", "crime rate", "crimes in", "total crimes"],
        "prediction": ["predict", "forecast", "future", "will there be", "expected crimes", "upcoming"],
        "safety_tips": ["safety", "tips", "how to stay safe", "protect", "prevention", "avoid crime"],
        "report_crime": ["report", "submit", "witnessed", "victim", "incident"],
        "emergency": ["emergency", "help", "urgent", "danger", "911", "police now"],
        "location_safety": ["safe area", "dangerous", "safest route", "area safety", "neighborhood"]
    }
    
    for intent_name, keywords in intents.items():
        if any(keyword in message for keyword in keywords):
            return intent_name
    
    return "general"


async def _handle_crime_stats(db: Session, message: str) -> dict:
    """Handle crime statistics query"""
    # Extract time period if mentioned
    days = 30
    if "week" in message:
        days = 7
    elif "month" in message:
        days = 30
    elif "year" in message:
        days = 365
    
    stats = crime_service.get_crime_stats(db, days)
    return stats


def _format_crime_stats_response(data: dict) -> str:
    """Format crime statistics into readable text"""
    response = f"📊 Crime Statistics (Last {data['period_days']} days):\n\n"
    response += f"Total Crimes: {data['total_crimes']}\n"
    response += f"Arrests Made: {data['arrests']} ({data['arrest_rate']}%)\n\n"
    
    if data['by_type']:
        response += "Top Crime Types:\n"
        for item in data['by_type'][:5]:
            response += f"  • {item['type']}: {item['count']}\n"
    
    return response


async def _handle_prediction_query(db: Session, message: str) -> dict:
    """Handle crime prediction query"""
    # Simple prediction for the next 7 days
    request = schemas.PredictionRequest(days_ahead=7)
    prediction = await prediction_service.predict_crimes(db, request)
    
    return {
        "predictions": prediction.predictions,
        "accuracy": prediction.model_accuracy
    }


def _format_prediction_response(data: dict) -> str:
    """Format prediction into readable text"""
    response = "🔮 Crime Predictions:\n\n"
    
    for pred in data['predictions'][:3]:  # Show first 3 days
        response += f"{pred['date']}: ~{pred['predicted_crimes']} crimes expected\n"
    
    response += f"\nModel Accuracy: {data['accuracy']:.1f}%\n"
    response += "\nNote: Predictions are based on historical patterns and may vary."
    
    return response


def _get_safety_tips() -> str:
    """Return safety tips"""
    tips = [
        "🔒 Always lock your doors and windows",
        "💡 Keep outdoor areas well-lit at night",
        "👀 Be aware of your surroundings",
        "📱 Share your location with trusted contacts",
        "🚗 Park in well-lit, populated areas",
        "🏠 Use security systems and cameras",
        "👥 Walk in groups when possible",
        "🚨 Report suspicious activity immediately"
    ]
    return "🛡️ Safety Tips:\n\n" + "\n".join(tips)


def _get_report_instructions() -> str:
    """Return crime reporting instructions"""
    return (
        "📝 To report a crime:\n\n"
        "1. Click the 'Report Crime' button on the map\n"
        "2. Select the crime type and location\n"
        "3. Provide a description and any evidence\n"
        "4. Submit your report\n\n"
        "For emergencies, call 911 immediately!"
    )


def _get_emergency_info() -> str:
    """Return emergency contact information"""
    return (
        "🚨 Emergency Contacts:\n\n"
        "Police: 911\n"
        "Fire Department: 911\n"
        "Ambulance: 911\n\n"
        "Non-Emergency Police: 311\n\n"
        "Stay safe and help is on the way!"
    )


async def _handle_location_safety(db: Session, message: str) -> dict:
    """Handle location safety query"""
    # Get recent crimes
    start_date = datetime.utcnow() - timedelta(days=30)
    recent_crimes = crime_service.get_crimes(db, start_date=start_date, limit=1000)
    
    return {
        "total_incidents": len(recent_crimes),
        "period": "30 days"
    }


def _format_location_safety_response(data: dict) -> str:
    """Format location safety into readable text"""
    return (
        f"🗺️ Area Safety Information:\n\n"
        f"Recent Incidents (30 days): {data['total_incidents']}\n\n"
        f"💡 Tip: Use the 'Safety Route Planner' to find the safest path to your destination!"
    )


def _get_default_response() -> str:
    """Return default response for unrecognized queries"""
    return (
        "👋 Hello! I'm your crime information assistant.\n\n"
        "I can help you with:\n"
        "• Crime statistics and trends\n"
        "• Crime predictions and forecasts\n"
        "• Safety tips and advice\n"
        "• Reporting crimes\n"
        "• Emergency information\n\n"
        "What would you like to know?"
    )
