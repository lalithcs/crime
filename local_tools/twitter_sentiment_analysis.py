"""
Local Twitter Sentiment Analysis for Crime Hotspot Prediction
Run this script locally to analyze tweets from Hyderabad areas
and generate crime hotspot predictions based on negative sentiment.
"""
import tweepy
import pandas as pd
from datetime import datetime, timedelta
from textblob import TextBlob
from collections import defaultdict
import json
import os

# Twitter API Credentials (get from https://developer.twitter.com)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "your_api_key_here")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "your_api_secret_here")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "your_access_token_here")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "your_access_secret_here")

# Hyderabad areas with coordinates
HYDERABAD_AREAS = {
    "Madhapur": {"lat": 17.450, "lng": 78.390, "radius_km": 2},
    "Gachibowli": {"lat": 17.440, "lng": 78.355, "radius_km": 2},
    "Hitech City": {"lat": 17.450, "lng": 78.380, "radius_km": 2},
    "Begumpet": {"lat": 17.445, "lng": 78.468, "radius_km": 2},
    "Secunderabad": {"lat": 17.440, "lng": 78.503, "radius_km": 2},
    "Banjara Hills": {"lat": 17.418, "lng": 78.448, "radius_km": 2},
    "Kukatpally": {"lat": 17.493, "lng": 78.398, "radius_km": 2},
    "LB Nagar": {"lat": 17.343, "lng": 78.553, "radius_km": 2},
    "Dilsukhnagar": {"lat": 17.373, "lng": 78.528, "radius_km": 2},
    "Charminar": {"lat": 17.363, "lng": 78.473, "radius_km": 2},
}

# Crime-related keywords to filter tweets
CRIME_KEYWORDS = [
    "theft", "robbery", "stolen", "crime", "assault", "harassment",
    "unsafe", "danger", "scared", "fear", "police", "security",
    "incident", "attack", "violence", "burglar", "chain snatching",
    "eve teasing", "kidnap", "fraud", "scam"
]


def authenticate_twitter():
    """Authenticate with Twitter API"""
    try:
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        api.verify_credentials()
        print("✓ Twitter authentication successful!")
        return api
    except Exception as e:
        print(f"✗ Twitter authentication failed: {e}")
        return None


def fetch_area_tweets(api, area_name, area_data, days_back=7):
    """Fetch tweets from a specific area"""
    print(f"\nFetching tweets for {area_name}...")
    
    # Create geocode query (lat,lng,radius)
    geocode = f"{area_data['lat']},{area_data['lng']},{area_data['radius_km']}km"
    
    # Search for crime-related tweets
    query = " OR ".join(CRIME_KEYWORDS) + " -filter:retweets"
    
    tweets = []
    try:
        for tweet in tweepy.Cursor(
            api.search_tweets,
            q=query,
            geocode=geocode,
            lang="en",
            tweet_mode="extended",
            count=100
        ).items(200):  # Fetch up to 200 tweets
            
            # Filter by date
            if tweet.created_at > datetime.now() - timedelta(days=days_back):
                tweets.append({
                    "text": tweet.full_text,
                    "created_at": tweet.created_at,
                    "location": area_name,
                    "lat": area_data['lat'],
                    "lng": area_data['lng'],
                    "user": tweet.user.screen_name,
                    "id": tweet.id
                })
        
        print(f"  → Found {len(tweets)} tweets")
        return tweets
    
    except Exception as e:
        print(f"  ✗ Error fetching tweets: {e}")
        return []


def analyze_sentiment(text):
    """Analyze sentiment using TextBlob (simple & fast)"""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
        
        if polarity < -0.1:
            sentiment = "negative"
        elif polarity > 0.1:
            sentiment = "positive"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": blob.sentiment.subjectivity
        }
    except:
        return {"sentiment": "neutral", "polarity": 0, "subjectivity": 0}


def generate_hotspots(tweets_data):
    """Generate crime hotspot predictions based on tweet sentiment"""
    print("\n📊 Analyzing sentiment and generating hotspots...")
    
    area_scores = defaultdict(lambda: {
        "total_tweets": 0,
        "negative_tweets": 0,
        "avg_polarity": 0,
        "risk_score": 0,
        "tweets": []
    })
    
    # Analyze each tweet
    for tweet in tweets_data:
        sentiment = analyze_sentiment(tweet['text'])
        tweet['sentiment'] = sentiment
        
        area = tweet['location']
        area_scores[area]['total_tweets'] += 1
        area_scores[area]['tweets'].append(tweet)
        
        if sentiment['sentiment'] == 'negative':
            area_scores[area]['negative_tweets'] += 1
    
    # Calculate risk scores
    hotspots = []
    for area, data in area_scores.items():
        if data['total_tweets'] > 0:
            negative_ratio = data['negative_tweets'] / data['total_tweets']
            
            # Calculate average polarity
            polarities = [t['sentiment']['polarity'] for t in data['tweets']]
            avg_polarity = sum(polarities) / len(polarities)
            
            # Risk score: higher negative ratio + lower polarity = higher risk
            risk_score = (negative_ratio * 100) - (avg_polarity * 50)
            
            hotspots.append({
                "area": area,
                "lat": data['tweets'][0]['lat'],
                "lng": data['tweets'][0]['lng'],
                "total_tweets": data['total_tweets'],
                "negative_tweets": data['negative_tweets'],
                "negative_ratio": round(negative_ratio * 100, 2),
                "avg_polarity": round(avg_polarity, 3),
                "risk_score": round(risk_score, 2),
                "severity": "high" if risk_score > 50 else "medium" if risk_score > 25 else "low",
                "predicted_crime_increase": round(negative_ratio * 30, 1)  # Predict 0-30% increase
            })
    
    # Sort by risk score
    hotspots.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return hotspots


def save_results(tweets_data, hotspots):
    """Save results to JSON files"""
    output_dir = "twitter_analysis_output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save tweets
    tweets_file = f"{output_dir}/tweets_{timestamp}.json"
    with open(tweets_file, 'w', encoding='utf-8') as f:
        json.dump(tweets_data, f, indent=2, default=str)
    print(f"\n✓ Saved tweets to: {tweets_file}")
    
    # Save hotspots
    hotspots_file = f"{output_dir}/hotspots_{timestamp}.json"
    with open(hotspots_file, 'w', encoding='utf-8') as f:
        json.dump(hotspots, f, indent=2)
    print(f"✓ Saved hotspots to: {hotspots_file}")
    
    # Create summary CSV
    df = pd.DataFrame(hotspots)
    csv_file = f"{output_dir}/hotspots_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"✓ Saved CSV to: {csv_file}")
    
    return hotspots_file


def print_summary(hotspots):
    """Print summary of results"""
    print("\n" + "="*60)
    print("📍 CRIME HOTSPOT PREDICTIONS (Based on Twitter Sentiment)")
    print("="*60)
    
    for idx, spot in enumerate(hotspots, 1):
        print(f"\n{idx}. {spot['area']}")
        print(f"   Risk Score: {spot['risk_score']} ({spot['severity'].upper()})")
        print(f"   Negative Sentiment: {spot['negative_ratio']}% ({spot['negative_tweets']}/{spot['total_tweets']} tweets)")
        print(f"   Avg Polarity: {spot['avg_polarity']}")
        print(f"   Predicted Crime Increase: +{spot['predicted_crime_increase']}%")
    
    print("\n" + "="*60)


def main():
    """Main execution"""
    print("🐦 Twitter Sentiment Analysis for Crime Hotspot Prediction")
    print("="*60)
    
    # Authenticate
    api = authenticate_twitter()
    if not api:
        print("\n❌ Cannot proceed without Twitter API credentials.")
        print("\nTo use this tool:")
        print("1. Get Twitter API credentials from: https://developer.twitter.com")
        print("2. Set environment variables:")
        print("   TWITTER_API_KEY=your_api_key")
        print("   TWITTER_API_SECRET=your_api_secret")
        print("   TWITTER_ACCESS_TOKEN=your_access_token")
        print("   TWITTER_ACCESS_SECRET=your_access_secret")
        return
    
    # Fetch tweets from all areas
    all_tweets = []
    for area_name, area_data in HYDERABAD_AREAS.items():
        tweets = fetch_area_tweets(api, area_name, area_data, days_back=7)
        all_tweets.extend(tweets)
    
    if not all_tweets:
        print("\n⚠️ No tweets found. Try:")
        print("   - Expanding date range")
        print("   - Adding more keywords")
        print("   - Using different areas")
        return
    
    print(f"\n📊 Total tweets collected: {len(all_tweets)}")
    
    # Generate hotspots
    hotspots = generate_hotspots(all_tweets)
    
    # Save results
    hotspots_file = save_results(all_tweets, hotspots)
    
    # Print summary
    print_summary(hotspots)
    
    print(f"\n✓ Analysis complete! Results saved to: twitter_analysis_output/")
    print(f"\nTo use these hotspots in your platform:")
    print(f"1. Upload {hotspots_file} to your backend")
    print(f"2. API will display these as predicted hotspots on the map")


if __name__ == "__main__":
    main()
