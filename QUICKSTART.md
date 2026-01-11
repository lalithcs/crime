# 🚀 Quick Start Guide

## Getting Started in 5 Minutes

### Prerequisites
- Windows 10/11 OR Linux/Mac
- Docker Desktop installed (recommended) OR Python 3.10+ and Node.js 18+

---

## ⚡ Option 1: Docker (Easiest - Recommended)

### Windows
```powershell
cd e:\nikhil\crime-safety-platform
.\start.bat
```

### Linux/Mac
```bash
cd crime-safety-platform
chmod +x start.sh
./start.sh
```

**That's it!** Wait 2-3 minutes and visit:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🛠️ Option 2: Manual Setup (Development)

### Step 1: Backend

```bash
# Navigate to backend
cd crime-safety-platform/backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create database (uses SQLite by default)
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Load sample data
python scripts/ingest_data.py

# Start backend
uvicorn app.main:app --reload
```

Backend will run on http://localhost:8000

### Step 2: Frontend

**Open a NEW terminal:**

```bash
# Navigate to frontend
cd crime-safety-platform/frontend

# Install dependencies
npm install

# Start frontend
npm start
```

Frontend will run on http://localhost:3000

---

## 🎯 Features Overview

### 1. **Live Crime Map** 📍
- Real-time visualization of crimes and user reports
- Filter by crime type, date range, location
- WebSocket updates for instant notifications

### 2. **User Reporting** 📝
- Click "Report Crime" button
- Fill in details (type, description, location)
- Use GPS or enter coordinates manually
- Reports appear instantly on map

### 3. **ARIMA Predictions** 🔮
- Navigate to Dashboard tab
- View 7-day crime forecasts
- See predicted hotspots
- Model accuracy displayed

### 4. **Safety Route Planner** 🛣️
- Navigate to "Safe Routes" tab
- Enter start and destination coordinates
- System calculates route avoiding crime zones
- Compare safe vs direct routes
- **Fixed**: Routing logic now properly avoids high-crime areas

### 5. **Sentiment Analysis** 📊
- Navigate to "Sentiment" tab
- Enter citizen feedback text
- NLP model analyzes sentiment (positive/negative/neutral)
- View trends over time

### 6. **Crime Chatbot** 💬
- Click chatbot icon (bottom-right)
- Ask about:
  - Crime statistics
  - Predictions
  - Safety tips
  - How to report crimes
  - Emergency info

### 7. **Community Alerts** 🚨
- Alerts panel in top-right
- Auto-generated based on crime spikes
- Real-time notifications
- Severity levels (low/medium/high/critical)

### 8. **Environmental Factors** 🏗️
- Poor lighting areas marked on map
- Construction zones highlighted
- Abandoned buildings tracked
- Correlation with crime rates

---

## 📊 Test the Platform

### Test Crime Reporting
1. Click "Report Crime"
2. Select crime type: "THEFT"
3. Description: "Test incident"
4. Use current location or enter: 41.8781, -87.6298
5. Submit
6. ✅ Report appears on map immediately

### Test Predictions
1. Go to Dashboard
2. Scroll to "7-Day Crime Forecast"
3. ✅ See predicted crime counts
4. ✅ View confidence intervals

### Test Safety Route
1. Go to "Safe Routes"
2. Start: 41.8781, -87.6298
3. End: 41.9, -87.65
4. Radius: 0.5 km
5. Click "Calculate Safe Route"
6. ✅ Route appears avoiding crime zones
7. ✅ Safety score and avoided zones displayed

### Test Sentiment
1. Go to "Sentiment" tab
2. Enter: "I feel very safe in this neighborhood"
3. Click "Analyze"
4. ✅ Shows POSITIVE sentiment
5. Try: "Crime is terrible here"
6. ✅ Shows NEGATIVE sentiment

### Test Chatbot
1. Click chatbot icon
2. Ask: "Show me crime statistics"
3. ✅ Bot responds with stats
4. Ask: "Give me safety tips"
5. ✅ Bot provides tips

---

## 🔧 Troubleshooting

### Issue: Backend won't start
**Solution:**
```bash
# Check if port 8000 is in use
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# Kill the process or use different port
uvicorn app.main:app --reload --port 8001
```

### Issue: Frontend won't start
**Solution:**
```bash
# Check if port 3000 is in use
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

### Issue: No crime data on map
**Solution:**
```bash
# Reload sample data
cd backend
python scripts/ingest_data.py
```

### Issue: WebSocket not connecting
**Solution:**
- Make sure backend is running
- Check browser console for errors
- Verify WebSocket URL in code matches backend

### Issue: Map not loading
**Solution:**
- Check internet connection (map tiles from OpenStreetMap)
- Check browser console for errors
- Try refreshing the page

---

## 📚 Next Steps

1. **Customize Dataset**: Replace synthetic data with real crime data
2. **Add Authentication**: Implement user login/registration
3. **API Keys**: Add OpenRouteService API key for better routing
4. **Deploy**: Follow [DEPLOYMENT.md](DEPLOYMENT.md) for production
5. **Test**: Follow [TESTING.md](TESTING.md) for comprehensive testing

---

## 🎓 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────┬──────────┬───────────┬─────────┬────────────┐ │
│  │ Live Map │Dashboard │Safe Routes│Sentiment│  Chatbot   │ │
│  └──────────┴──────────┴───────────┴─────────┴────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP + WebSocket
┌───────────────────────────▼─────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌─────────┬───────────┬────────────┬──────────┬─────────┐  │
│  │ Crimes  │Predictions│   Routes   │Sentiment │Chatbot  │  │
│  │Reports  │(ARIMA ML) │(Avoidance) │  (NLP)   │(Rules)  │  │
│  └─────────┴───────────┴────────────┴──────────┴─────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
┌───▼──────┐        ┌──────▼──────┐       ┌───────▼─────┐
│PostgreSQL│        │    Redis    │       │  External   │
│ Database │        │   (Cache)   │       │   APIs      │
└──────────┘        └─────────────┘       └─────────────┘
```

---

## 🤝 Support

- **Documentation**: See [README.md](README.md)
- **Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Testing**: See [TESTING.md](TESTING.md)

---

## ✅ All Features Implemented

✅ Real-time live dashboard/map  
✅ User crime reporting with map visualization  
✅ ARIMA Model for time-series prediction  
✅ Community alert engine  
✅ Safety Route Planner (with fixed routing logic)  
✅ NLP Sentiment analysis  
✅ Crime chatbot  
✅ Crime cause mapper (environmental factors)  
✅ Dataset ingestion (Chicago Crime Data + synthetic fallback)  
✅ WebSocket real-time updates  
✅ Docker deployment ready  

---

**🎉 Enjoy your Crime Prediction & Safety Platform!**
