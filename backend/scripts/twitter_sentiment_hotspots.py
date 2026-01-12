"""
Twitter Sentiment Analysis for Crime Hotspot Prediction
Fetches tweets from Hyderabad areas and predicts crime hotspots based on sentiment
Run locally: python twitter_sentiment_hotspots.py
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os

# Twitter API v2 credentials (get from https://developer.twitter.com)
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_BEARER_TOKEN")

# Hyderabad areas with coordinates
HYDERABAD_AREAS = {
    "Madhapur": {"lat": 17.450, "lng": 78.392, "radius_km": 2},
    "Gachibowli": {"lat": 17.440, "lng": 78.352, "radius_km": 2},
    "Hitech City": {"lat": 17.450, "lng": 78.380, "radius_km": 2},
    "Begumpet": {"lat": 17.445, "lng": 78.467, "radius_km": 2},
    "Secunderabad": {"lat": 17.440, "lng": 78.502, "radius_km": 2},
    "Banjara Hills": {"lat": 17.417, "lng": 78.447, "radius_km": 2},
    "Kukatpally": {"lat": 17.492, "lng": 78.397, "radius_km": 2},
    "Dilsukhnagar": {"lat": 17.372, "lng": 78.527, "radius_km": 2},
    "Charminar": {"lat": 17.362, "lng": 78.472, "radius_km": 2},
    "Uppal": {"lat": 17.402, "lng": 78.557, "radius_km": 2},
}

# Crime-related keywords
CRIME_KEYWORDS = [
    "theft", "robbery", "burglary", "assault", "crime", "unsafe", "dangerous",
    "police", "incident", "violence", "attack", "steal", "mugging", "fear",
    "चोरी", "लूट", "अपराध", "असुरक्षित"  # Hindi keywords
]


def fetch_tweets_by_location(area_name: str, lat: float, lng: float, radius_km: int, max_tweets: int = 100) -> List[Dict]:
    """
    Fetch tweets from a specific location using Twitter API v2
    Note: Requires Twitter API v2 access (Free tier available)
    """
    if TWITTER_BEARER_TOKEN == "YOUR_TWITTER_BEARER_TOKEN":
        print("⚠️  Twitter API token not configured. Using mock data.")
        return generate_mock_tweets(area_name, max_tweets)
    
    url = "https://api.twitter.com/2/tweets/search/recent"
    
    # Build query with location and crime keywords
    query = f"({' OR '.join(CRIME_KEYWORDS)}) point_radius:[{lng} {lat} {radius_km}km]"
    
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    params = {
        "query": query,
        "max_results": min(max_tweets, 100),  # API limit
        "tweet.fields": "created_at,text,geo,lang",
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        tweets = []
        if "data" in data:
            for tweet in data["data"]:
                tweets.append({
                    "text": tweet["text"],
                    "created_at": tweet["created_at"],
                    "area": area_name,
                    "lat": lat,
                    "lng": lng,
                })
        
        print(f"✅ Fetched {len(tweets)} tweets from {area_name}")
        return tweets
        
    except Exception as e:
        print(f"❌ Error fetching tweets: {e}")
        return generate_mock_tweets(area_name, max_tweets)


def generate_mock_tweets(area_name: str, count: int = 20) -> List[Dict]:
    """Generate mock tweets for testing without API access"""
    import random
    
    mock_tweets = [
        f"Feeling unsafe walking at night near {area_name}",
        f"Another theft incident reported in {area_name} area",
        f"Police presence needed in {area_name}",
        f"Love the new park in {area_name}, feels very safe",
        f"Great community in {area_name}, everyone looks out for each other",
        f"Witnessed a robbery near {area_name} metro station",
        f"Car break-in reported in {area_name} parking lot",
        f"{area_name} is becoming unsafe at night",
        f"More street lights needed in {area_name}",
        f"Excellent security in {area_name} apartments",
        f"Chain snatching incident near {area_name}",
        f"{area_name} is a peaceful neighborhood",
        f"Crime rate increasing in {area_name}",
        f"Safe and clean area, {area_name} rocks!",
        f"Need more police patrolling in {area_name}",
    ]
    
    tweets = []
    for i in range(count):
        tweets.append({
            "text": random.choice(mock_tweets),
            "created_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "area": area_name,
            "lat": HYDERABAD_AREAS[area_name]["lat"],
            "lng": HYDERABAD_AREAS[area_name]["lng"],
        })
    
    return tweets


def analyze_tweet_sentiment(text: str) -> Dict:
    """
    Simple keyword-based sentiment analysis
    Returns sentiment score: -1 (very negative) to +1 (very positive)
    """
    negative_keywords = [
        "unsafe", "crime", "theft", "robbery", "dangerous", "fear", "attack",
        "steal", "violence", "incident", "scared", "worried", "afraid",
        "चोरी", "लूट", "असुरक्षित", "खतरनाक"
    ]
    
    positive_keywords = [
        "safe", "secure", "peaceful", "clean", "good", "great", "excellent",
        "love", "beautiful", "friendly", "nice", "happy", "protected"
    ]
    
    text_lower = text.lower()
    
    negative_count = sum(1 for word in negative_keywords if word in text_lower)
    positive_count = sum(1 for word in positive_keywords if word in text_lower)
    
    # Calculate score
    if negative_count + positive_count == 0:
        return {"sentiment": "neutral", "score": 0.0, "confidence": 0.5}
    
    score = (positive_count - negative_count) / (positive_count + negative_count)
    
    if score < -0.3:
        sentiment = "negative"
    elif score > 0.3:
        sentiment = "positive"
    else:
        sentiment = "neutral"
    
    confidence = min(abs(score) + 0.5, 1.0)
    
    return {
        "sentiment": sentiment,
        "score": score,
        "confidence": confidence,
        "negative_keywords": negative_count,
        "positive_keywords": positive_count,
    }


def generate_hotspots_from_sentiment(area_results: List[Dict]) -> List[Dict]:
    """
    Generate crime hotspots based on negative sentiment
    Areas with high negative sentiment = potential crime hotspots
    """
    hotspots = []
    
    for area in area_results:
        # Calculate risk score (0-100)
        # High negative sentiment + many tweets = high risk
        avg_sentiment = area["avg_sentiment_score"]
        negative_ratio = area["negative_tweets"] / max(area["total_tweets"], 1)
        
        # Risk score: combine negative sentiment and negative tweet ratio
        risk_score = (1 - avg_sentiment) * 50 + (negative_ratio * 50)
        
        # Determine severity
        if risk_score > 70:
            severity = "high"
        elif risk_score > 40:
            severity = "medium"
        else:
            severity = "low"
        
        hotspots.append({
            "area": area["area_name"],
            "latitude": area["lat"],
            "longitude": area["lng"],
            "risk_score": round(risk_score, 1),
            "severity": severity,
            "total_tweets": area["total_tweets"],
            "negative_tweets": area["negative_tweets"],
            "avg_sentiment_score": round(avg_sentiment, 2),
            "predicted_crime_increase": round(risk_score * 0.5, 1),  # Correlation: higher risk = more crimes
        })
    
    # Sort by risk score
    hotspots.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return hotspots


def main():
    print("🔍 Twitter Sentiment Analysis for Crime Hotspot Prediction")
    print("=" * 60)
    print(f"Analyzing {len(HYDERABAD_AREAS)} areas in Hyderabad...\n")
    
    all_tweets = []
    area_results = []
    
    # Fetch and analyze tweets for each area
    for area_name, coords in HYDERABAD_AREAS.items():
        print(f"\n📍 Processing {area_name}...")
        
        # Fetch tweets
        tweets = fetch_tweets_by_location(
            area_name=area_name,
            lat=coords["lat"],
            lng=coords["lng"],
            radius_km=coords["radius_km"],
            max_tweets=50
        )
        
        if not tweets:
            print(f"   ⚠️  No tweets found for {area_name}")
            continue
        
        # Analyze sentiment for each tweet
        sentiments = []
        negative_count = 0
        
        for tweet in tweets:
            analysis = analyze_tweet_sentiment(tweet["text"])
            tweet["sentiment"] = analysis
            sentiments.append(analysis["score"])
            
            if analysis["sentiment"] == "negative":
                negative_count += 1
                print(f"   ⚠️  Negative: {tweet['text'][:60]}...")
        
        # Calculate area statistics
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        area_results.append({
            "area_name": area_name,
            "lat": coords["lat"],
            "lng": coords["lng"],
            "total_tweets": len(tweets),
            "negative_tweets": negative_count,
            "avg_sentiment_score": avg_sentiment,
        })
        
        all_tweets.extend(tweets)
        
        print(f"   📊 Analyzed {len(tweets)} tweets")
        print(f"   📈 Avg Sentiment: {avg_sentiment:.2f}")
        print(f"   ⚠️  Negative tweets: {negative_count}")
    
    # Generate hotspots
    print("\n" + "=" * 60)
    print("🔥 CRIME HOTSPOT PREDICTIONS (Based on Twitter Sentiment)")
    print("=" * 60 + "\n")
    
    hotspots = generate_hotspots_from_sentiment(area_results)
    
    print(f"{'Rank':<6} {'Area':<18} {'Risk Score':<12} {'Severity':<10} {'Tweets':<8} {'Negative'}")
    print("-" * 70)
    
    for idx, hotspot in enumerate(hotspots, 1):
        print(f"{idx:<6} {hotspot['area']:<18} {hotspot['risk_score']:<12} "
              f"{hotspot['severity'].upper():<10} {hotspot['total_tweets']:<8} {hotspot['negative_tweets']}")
    
    # Save results to JSON
    output = {
        "analysis_date": datetime.utcnow().isoformat(),
        "total_tweets_analyzed": len(all_tweets),
        "total_areas": len(HYDERABAD_AREAS),
        "hotspots": hotspots,
        "detailed_results": area_results,
    }
    
    output_file = "twitter_sentiment_hotspots.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Results saved to {output_file}")
    print("\n💡 Integration Steps:")
    print("1. Load this data into your backend: POST /api/predictions/import-twitter-hotspots")
    print("2. View on Dashboard → Hotspots will show sentiment-based predictions")
    print("3. Crime Map will highlight high-risk areas identified by Twitter sentiment")
    
    return hotspots


if __name__ == "__main__":
    main()
