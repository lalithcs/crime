# Twitter Sentiment-Based Crime Hotspot Prediction

## 🎯 Purpose
Analyze Twitter sentiment from Hyderabad areas to predict crime hotspots. Areas with high negative sentiment about safety = higher crime risk.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install requests
```

### 2. Run Locally (Without Twitter API - Uses Mock Data)
```bash
python scripts/twitter_sentiment_hotspots.py
```

### 3. With Real Twitter Data (Optional)
Get free Twitter API access: https://developer.twitter.com/en/portal/dashboard

Set environment variable:
```bash
# Windows
set TWITTER_BEARER_TOKEN=your_token_here

# Linux/Mac
export TWITTER_BEARER_TOKEN=your_token_here
```

Then run:
```bash
python scripts/twitter_sentiment_hotspots.py
```

## 📊 How It Works

### Step 1: Fetch Tweets by Location
- Searches tweets within 2km radius of each Hyderabad area
- Looks for crime-related keywords: "theft", "robbery", "unsafe", "crime", etc.
- Also includes Hindi keywords: "चोरी", "लूट", "असुरक्षित"

### Step 2: Sentiment Analysis
Each tweet is analyzed for:
- **Negative keywords**: unsafe, crime, theft, robbery, dangerous, fear
- **Positive keywords**: safe, secure, peaceful, clean, good, protected

Sentiment Score: -1 (very negative) to +1 (very positive)

### Step 3: Generate Hotspots
Risk Score = (1 - avg_sentiment) × 50 + (negative_ratio × 50)

**Severity Levels:**
- High Risk (70-100): Areas with many negative safety tweets
- Medium Risk (40-70): Some concerns reported
- Low Risk (0-40): Generally positive sentiment

### Step 4: Predict Crime Increase
Predicted Crime Increase = Risk Score × 0.5

Example: Risk Score 80 → Predicted 40% crime increase

## 📈 Sample Output

```
🔥 CRIME HOTSPOT PREDICTIONS (Based on Twitter Sentiment)
================================================================

Rank   Area              Risk Score   Severity   Tweets   Negative
----------------------------------------------------------------------
1      Charminar         85.3         HIGH       42       28
2      Dilsukhnagar      72.1         HIGH       38       24
3      Kukatpally        58.4         MEDIUM     35       18
4      Secunderabad      45.2         MEDIUM     40       16
5      Madhapur          32.8         LOW        45       12
```

## 🔗 Integration with Platform

### Option 1: Manual Import
1. Run script → generates `twitter_sentiment_hotspots.json`
2. Copy hotspots to backend database
3. Dashboard shows Twitter-based predictions

### Option 2: API Endpoint (TODO)
Create endpoint to import Twitter hotspots:
```python
@predictions_router.post("/import-twitter-hotspots")
async def import_twitter_hotspots(file: UploadFile, db: Session = Depends(get_db)):
    # Parse JSON
    # Save hotspots to database
    # Return success
```

## 📋 Areas Analyzed

1. **Madhapur** - Tech hub
2. **Gachibowli** - IT corridor
3. **Hitech City** - Business district
4. **Begumpet** - Residential + commercial
5. **Secunderabad** - Major railway junction
6. **Banjara Hills** - Upscale residential
7. **Kukatpally** - Dense residential
8. **Dilsukhnagar** - Shopping area
9. **Charminar** - Old city
10. **Uppal** - Residential + industrial

## 🎓 Technical Details

### Twitter API Requirements
- **Free Tier**: 500,000 tweets/month
- **Endpoint**: `/2/tweets/search/recent`
- **Geo Search**: `point_radius:[lng lat radius]`

### Mock Data Mode
If Twitter API not configured:
- Generates realistic mock tweets
- 20 tweets per area
- Mix of positive and negative sentiments
- Useful for testing and demo

## 💡 Use Cases

1. **Early Warning System**: Detect areas where citizens report safety concerns
2. **Resource Allocation**: Deploy police to areas with negative sentiment spikes
3. **Trend Analysis**: Compare Twitter sentiment vs actual crime data
4. **Community Engagement**: Understand citizen perceptions of safety

## 🔒 Privacy & Ethics
- Only analyzes publicly available tweets
- No personal data stored
- Aggregated area-level statistics only
- Follows Twitter API terms of service

## 📦 Output File

`twitter_sentiment_hotspots.json`:
```json
{
  "analysis_date": "2026-01-12T03:30:00",
  "total_tweets_analyzed": 420,
  "hotspots": [
    {
      "area": "Charminar",
      "latitude": 17.362,
      "longitude": 78.472,
      "risk_score": 85.3,
      "severity": "high",
      "predicted_crime_increase": 42.6
    }
  ]
}
```

## 🚀 Next Steps

1. Run script locally to see results
2. Integrate with Dashboard hotspots display
3. Compare Twitter sentiment hotspots vs ARIMA predictions
4. Combine both for more accurate predictions

---

**Note**: This runs locally, NOT on Render (to avoid API costs and token limits).
