# CrimeScope

A comprehensive real-time crime prediction and safety platform with ML-powered forecasting, community alerts, and intelligent route planning.

## Features

1. **Real-time Dashboard & Map** - Interactive crime visualization with live updates
2. **User Crime Reporting** - Citizens can report crimes visible on the map in real-time
3. **ARIMA Crime Prediction** - Time-series forecasting for proactive crime prevention
4. **Community Alert Engine** - Real-time notifications and alerts for citizens
5. **Safety Route Planner** - Intelligent routing that avoids high-crime areas
6. **Sentiment Analysis** - NLP-powered citizen sentiment monitoring
7. **Crime Chatbot** - AI assistant for crime queries and information
8. **Crime Cause Mapper** - Environmental factors (lighting, construction) tracking

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy
- **ML/AI**: ARIMA (statsmodels), scikit-learn, transformers (NLP)
- **Frontend**: React 18, Leaflet/Mapbox GL, TailwindCSS
- **Database**: PostgreSQL with PostGIS
- **Real-time**: WebSockets, Redis pub/sub
- **Routing**: OpenRouteService/OSRM API

## Project Structure

```
crime-safety-platform/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # Database models
│   │   ├── ml/          # ML models (ARIMA, NLP)
│   │   ├── services/    # Business logic
│   │   └── main.py      # Application entry
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API clients
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── data/                # Datasets and ML artifacts
├── docker-compose.yml
└── README.md
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup (Recommended)

```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Dataset

Using **Chicago Crime Dataset** (2001-2024) from data.cityofchicago.org
- 7M+ crime records
- Time-series compatible
- Geographic coordinates included

## API Endpoints

- `POST /api/reports` - Submit crime report
- `GET /api/crimes` - Get crimes with filters
- `GET /api/predictions` - Get ARIMA forecasts
- `POST /api/routes/safe` - Calculate safe route
- `POST /api/sentiment` - Analyze citizen sentiment
- `POST /api/chatbot` - Chat with crime bot
- `GET /api/alerts` - Get community alerts
- `GET /api/causes` - Get environmental factors

## Development

Run tests:
```bash
pytest backend/tests
npm test --prefix frontend
```

## License

MIT
