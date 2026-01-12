# 🐦 Twitter Sentiment Analysis Tool (Local)

## Purpose
Analyze tweets from Hyderabad areas to predict crime hotspots based on negative sentiment. Runs locally to avoid Render costs.

## Features
- Fetches geo-tagged tweets from 10 Hyderabad areas
- Filters crime-related tweets (theft, assault, harassment, etc.)
- Sentiment analysis using TextBlob
- Generates risk scores and predicted crime increases
- Exports hotspots as JSON/CSV

## Setup

### 1. Get Twitter API Credentials
1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Create a new app (Free tier is enough)
3. Get your credentials:
   - API Key
   - API Secret
   - Access Token
   - Access Secret

### 2. Install Dependencies
```powershell
cd e:\nikhil\crime-safety-platform\local_tools
pip install -r requirements.txt
```

### 3. Set Environment Variables
```powershell
# Windows PowerShell
$env:TWITTER_API_KEY="your_api_key_here"
$env:TWITTER_API_SECRET="your_api_secret_here"
$env:TWITTER_ACCESS_TOKEN="your_access_token_here"
$env:TWITTER_ACCESS_SECRET="your_access_secret_here"
```

Or edit the script directly and replace the credentials.

## Usage

### Run Analysis
```powershell
cd e:\nikhil\crime-safety-platform\local_tools
python twitter_sentiment_analysis.py
```

### Output
Creates `twitter_analysis_output/` folder with:
- `tweets_YYYYMMDD_HHMMSS.json` - Raw tweet data with sentiment
- `hotspots_YYYYMMDD_HHMMSS.json` - Predicted crime hotspots
- `hotspots_YYYYMMDD_HHMMSS.csv` - CSV for analysis

### Sample Output
```
📍 CRIME HOTSPOT PREDICTIONS (Based on Twitter Sentiment)
============================================================

1. Dilsukhnagar
   Risk Score: 65.3 (HIGH)
   Negative Sentiment: 45% (18/40 tweets)
   Predicted Crime Increase: +13.5%

2. Madhapur
   Risk Score: 42.8 (MEDIUM)
   Negative Sentiment: 32% (12/38 tweets)
   Predicted Crime Increase: +9.6%
```

## How It Works

### 1. Tweet Collection
- Searches tweets within 2km radius of each area
- Filters by crime keywords (theft, robbery, assault, etc.)
- Collects last 7 days of tweets

### 2. Sentiment Analysis
- TextBlob analyzes polarity (-1 to 1)
- Classifies as: Negative, Neutral, Positive
- Calculates average polarity per area

### 3. Risk Scoring
```
Risk Score = (Negative Ratio × 100) - (Avg Polarity × 50)
```
- Higher negative ratio → Higher risk
- Lower polarity → Higher risk
- Predicts crime increase: 0-30%

### 4. Severity Classification
- **HIGH**: Risk score > 50
- **MEDIUM**: Risk score 25-50
- **LOW**: Risk score < 25

## Integrating with Platform

### Option 1: Manual Upload
1. Run the analysis locally
2. Copy hotspots JSON to backend
3. Create API endpoint to import predictions

### Option 2: Scheduled Task
1. Run script weekly using Windows Task Scheduler
2. Auto-upload results to backend via API

## Configuration

### Adjust Areas
Edit `HYDERABAD_AREAS` in script to add/remove locations:
```python
HYDERABAD_AREAS = {
    "Your Area": {"lat": 17.xxx, "lng": 78.xxx, "radius_km": 2},
}
```

### Adjust Keywords
Edit `CRIME_KEYWORDS` to focus on specific crime types:
```python
CRIME_KEYWORDS = [
    "theft", "robbery", "assault", ...
]
```

### Adjust Date Range
Change `days_back` parameter:
```python
tweets = fetch_area_tweets(api, area_name, area_data, days_back=14)  # 14 days
```

## Troubleshooting

### No tweets found?
- Twitter Free tier has rate limits
- Try expanding search radius
- Use broader keywords
- Check if area has geo-tagged tweets

### Rate limit errors?
- Twitter API limits: 450 requests/15 min
- Script automatically waits (`wait_on_rate_limit=True`)
- Reduce number of areas if needed

### Authentication failed?
- Double-check credentials
- Ensure app has Read permissions
- Regenerate tokens if expired

## Advanced: Better Sentiment Analysis

For more accurate results, replace TextBlob with DistilBERT:

```python
# Install transformers
pip install transformers torch

# Replace analyze_sentiment function
from transformers import pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    result = sentiment_analyzer(text[:512])[0]
    return {
        "sentiment": result['label'].lower(),
        "polarity": result['score'] if result['label'] == 'POSITIVE' else -result['score']
    }
```

## Cost
- **FREE** - Runs on your local machine
- Twitter API Free tier: 500k tweets/month
- No Render costs

## Example Use Cases

### 1. Weekly Crime Forecast
Run every Sunday, predict hotspots for the week

### 2. Event-Based Analysis
After major incident, analyze sentiment surge

### 3. Police Resource Allocation
High-risk areas get more patrol coverage

### 4. Citizen Alerts
Auto-generate alerts for areas with negative sentiment spikes

---

**Ready to run!** Get your Twitter API credentials and start predicting crime hotspots from real citizen reports. 🚀
