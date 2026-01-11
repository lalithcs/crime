from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from transformers import pipeline
import torch

from app.models import crime, schemas


# Initialize sentiment analysis pipeline (using lightweight model)
try:
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=0 if torch.cuda.is_available() else -1
    )
except Exception as e:
    print(f"Warning: Could not load sentiment model: {e}")
    sentiment_analyzer = None


async def analyze_sentiment(db: Session, request: schemas.SentimentRequest) -> schemas.SentimentResponse:
    """
    Analyze sentiment of citizen text using NLP
    """
    if sentiment_analyzer is None:
        # Fallback to simple keyword-based sentiment
        return _simple_sentiment_analysis(db, request)
    
    try:
        # Truncate text to model's max length
        text = request.text[:512]
        
        # Run sentiment analysis
        result = sentiment_analyzer(text)[0]
        
        # Map labels
        sentiment_map = {
            "POSITIVE": "positive",
            "NEGATIVE": "negative",
            "NEUTRAL": "neutral"
        }
        
        sentiment = sentiment_map.get(result["label"], "neutral")
        score = result["score"]
        
        # Store sentiment in database
        db_sentiment = crime.Sentiment(
            text=request.text,
            sentiment=sentiment,
            sentiment_score=score if sentiment == "positive" else -score,
            location=request.location,
            latitude=request.latitude,
            longitude=request.longitude,
            source="user_report"
        )
        db.add(db_sentiment)
        db.commit()
        
        return schemas.SentimentResponse(
            sentiment=sentiment,
            sentiment_score=score if sentiment == "positive" else -score,
            confidence=score,
            text=request.text
        )
    
    except Exception as e:
        print(f"Sentiment analysis failed: {e}")
        return _simple_sentiment_analysis(db, request)


def _simple_sentiment_analysis(db: Session, request: schemas.SentimentRequest) -> schemas.SentimentResponse:
    """Simple keyword-based sentiment analysis as fallback"""
    text_lower = request.text.lower()
    
    # Simple keyword lists
    positive_words = ["safe", "good", "better", "improved", "happy", "secure", "peaceful", "clean"]
    negative_words = ["unsafe", "dangerous", "crime", "scared", "fear", "theft", "robbery", "bad", "worse"]
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if neg_count > pos_count:
        sentiment = "negative"
        score = -min(1.0, neg_count / 5)
    elif pos_count > neg_count:
        sentiment = "positive"
        score = min(1.0, pos_count / 5)
    else:
        sentiment = "neutral"
        score = 0.0
    
    # Store sentiment
    db_sentiment = crime.Sentiment(
        text=request.text,
        sentiment=sentiment,
        sentiment_score=score,
        location=request.location,
        latitude=request.latitude,
        longitude=request.longitude,
        source="user_report"
    )
    db.add(db_sentiment)
    db.commit()
    
    return schemas.SentimentResponse(
        sentiment=sentiment,
        sentiment_score=score,
        confidence=0.6,  # Lower confidence for simple method
        text=request.text
    )


def get_sentiment_trends(db: Session, days: int = 30, location: Optional[str] = None) -> dict:
    """Get sentiment trends over time"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(crime.Sentiment).filter(
        crime.Sentiment.created_at >= start_date
    )
    
    if location:
        query = query.filter(crime.Sentiment.location.ilike(f"%{location}%"))
    
    sentiments = query.all()
    
    if not sentiments:
        return {"message": "No sentiment data available", "trends": []}
    
    # Aggregate by sentiment type
    sentiment_counts = {
        "positive": sum(1 for s in sentiments if s.sentiment == "positive"),
        "negative": sum(1 for s in sentiments if s.sentiment == "negative"),
        "neutral": sum(1 for s in sentiments if s.sentiment == "neutral")
    }
    
    # Calculate average sentiment score
    avg_score = sum(s.sentiment_score for s in sentiments) / len(sentiments)
    
    # Trend over time (group by week)
    from collections import defaultdict
    weekly_sentiments = defaultdict(list)
    
    for s in sentiments:
        week = s.created_at.isocalendar()[1]  # Get week number
        weekly_sentiments[week].append(s.sentiment_score)
    
    weekly_trends = [
        {
            "week": week,
            "avg_sentiment": sum(scores) / len(scores),
            "count": len(scores)
        }
        for week, scores in sorted(weekly_sentiments.items())
    ]
    
    return {
        "period_days": days,
        "total_sentiments": len(sentiments),
        "sentiment_distribution": sentiment_counts,
        "average_sentiment_score": round(avg_score, 3),
        "overall_sentiment": "positive" if avg_score > 0.1 else "negative" if avg_score < -0.1 else "neutral",
        "weekly_trends": weekly_trends,
        "location": location
    }
