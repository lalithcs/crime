# Backend - CrimeScope API

This folder contains the FastAPI backend that powers CrimeScope's crime prediction, reporting, and routing capabilities.

---

## 📁 Folder Structure

```
backend/
├── app/
│   ├── __init__.py              # Empty file marking app as Python package
│   ├── main.py                  # FastAPI application entry point
│   ├── database.py              # SQLAlchemy database configuration
│   ├── api/
│   │   └── routes.py            # All REST API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── crime.py             # Crime SQLAlchemy model
│   │   └── schemas.py           # Pydantic validation schemas
│   └── services/
│       ├── __init__.py
│       ├── crime_service.py     # Crime data business logic
│       ├── prediction_service.py # ARIMA forecasting & hotspots
│       ├── route_service.py     # Safe route calculation
│       ├── chatbot_service.py   # AI chatbot responses
│       ├── notification_service.py # Email alerts
│       └── sentiment_service.py # Sentiment analysis (optional)
├── scripts/
│   └── ingest_data.py           # Generate synthetic crime data
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🔧 Core Files Explained

### 1. **main.py** - Application Entry Point

**Purpose**: Initializes FastAPI app, configures middleware, registers routes, handles startup/shutdown.

**Key Components**:

```python
# FastAPI app initialization
app = FastAPI(
    title="CrimeScope API",
    description="Real-time crime prediction and safety routing",
    version="1.0.0",
    lifespan=lifespan  # Startup/shutdown events
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event - runs when server starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CrimeScope API")
    Base.metadata.create_all(bind=engine)  # Create DB tables
    auto_load_data_if_empty()  # Load 1000 synthetic crimes if DB empty
    yield
    logger.info("Shutting down CrimeScope API")
```

**auto_load_data_if_empty() function**:
- Checks if database has any crime records
- If empty, generates 1000 synthetic crimes (700 Hyderabad + 300 Chicago)
- Commits in batches of 100 for performance
- Ensures platform always has data for demo/testing

**Route Registration**:
```python
app.include_router(routes.crimes_router, prefix="/api/crimes", tags=["Crimes"])
app.include_router(routes.reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(routes.predictions_router, prefix="/api/predictions", tags=["Predictions"])
# ... more routers
```

---

### 2. **database.py** - Database Configuration

**Purpose**: Sets up SQLAlchemy engine, session maker, and database connection.

```python
# SQLite (development) or PostgreSQL (production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crime_data.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session maker - creates new DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Dependency for route functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**How it works**:
1. `engine`: Manages connection pool to database
2. `SessionLocal`: Factory for creating database sessions
3. `Base`: Parent class for all SQLAlchemy models
4. `get_db()`: Dependency injection - provides DB session to routes, auto-closes after request

---

### 3. **api/routes.py** - API Endpoints

**Purpose**: Defines all REST API endpoints. Each router handles a specific domain.

**Structure**:

```python
# Create router for crimes
crimes_router = APIRouter()

@crimes_router.get("/", response_model=List[schemas.CrimeResponse])
def get_crimes(
    crime_type: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get crimes with optional filters"""
    crimes = crime_service.get_crimes(db, crime_type, days, limit)
    return crimes
```

**Key Endpoints**:

#### **Crimes Router** (`/api/crimes`)
- `GET /` - Get all crimes with filters (type, date range, limit)
- `GET /stats` - Crime statistics (count by type, severity, trend)
- `GET /heatmap` - Coordinates for heatmap visualization

#### **Reports Router** (`/api/reports`)
- `POST /` - Submit user crime report
- `GET /` - Get all user-submitted reports

#### **Predictions Router** (`/api/predictions`)
- `POST /` - Generate ARIMA forecast (7 or 30 days)
- `GET /hotspots` - Get top 10 crime hotspots using clustering

#### **Routes Router** (`/api/routes`)
- `POST /safe` - Calculate safe route avoiding crime zones

#### **Chatbot Router** (`/api/chatbot`)
- `POST /` - Send message to chatbot, get response

#### **Alerts Router** (`/api/alerts`)
- `GET /` - Get recent community alerts

#### **WebSocket** (`/ws/live`)
- Real-time crime updates pushed to clients

**Request Flow**:
1. Client sends HTTP request to endpoint
2. FastAPI validates request body using Pydantic schemas
3. Route function calls service layer (business logic)
4. Service queries database via SQLAlchemy
5. Response formatted according to response schema
6. JSON sent back to client

---

### 4. **models/crime.py** - Database Model

**Purpose**: Defines `Crime` table schema using SQLAlchemy ORM.

```python
class Crime(Base):
    __tablename__ = "crimes"
    
    id = Column(Integer, primary_key=True, index=True)
    crime_type = Column(String, index=True)  # theft, assault, etc.
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    occurred_at = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(Integer, default=1)  # 1=low, 2=medium, 3=high
    description = Column(Text, nullable=True)
    location_description = Column(String, nullable=True)
    status = Column(String, default="confirmed")  # confirmed, pending, false_report
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Key Features**:
- `index=True` on frequently queried columns (crime_type, occurred_at) for faster lookups
- `default` values for timestamps ensure records have creation dates
- `nullable=False` enforces required fields
- Supports both official crimes and user reports

---

### 5. **models/schemas.py** - Pydantic Validation

**Purpose**: Validates request/response data using Pydantic models.

```python
# Request schema - validates incoming data
class CrimeReportCreate(BaseModel):
    crime_type: str
    latitude: float
    longitude: float
    description: str
    severity: int = 1
    location_description: Optional[str] = None
    
    @validator('crime_type')
    def validate_crime_type(cls, v):
        allowed = ['theft', 'assault', 'robbery', 'burglary', ...]
        if v.lower() not in allowed:
            raise ValueError(f'Invalid crime type: {v}')
        return v.lower()

# Response schema - formats outgoing data
class CrimeResponse(BaseModel):
    id: int
    crime_type: str
    latitude: float
    longitude: float
    occurred_at: datetime
    severity: int
    description: Optional[str]
    
    class Config:
        orm_mode = True  # Allows conversion from SQLAlchemy model
```

**Benefits**:
- Automatic data validation
- Type checking at runtime
- Clear API documentation (appears in `/docs`)
- Prevents invalid data from reaching database

---

### 6. **services/crime_service.py** - Crime Data Logic

**Purpose**: Business logic for querying and processing crime data.

**Key Functions**:

```python
def get_crimes(db: Session, crime_type: Optional[str], days: int, limit: int):
    """Get crimes with filters"""
    query = db.query(Crime)
    
    # Filter by type
    if crime_type:
        query = query.filter(Crime.crime_type == crime_type)
    
    # Filter by date range
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(Crime.occurred_at >= cutoff_date)
    
    # Order by most recent first
    query = query.order_by(Crime.occurred_at.desc())
    
    # Limit results
    return query.limit(limit).all()

def get_crime_stats(db: Session, days: int):
    """Calculate crime statistics"""
    crimes = get_crimes(db, None, days, 10000)
    
    stats = {
        "total": len(crimes),
        "by_type": Counter(c.crime_type for c in crimes),
        "by_severity": Counter(c.severity for c in crimes),
        "avg_per_day": len(crimes) / days
    }
    return stats

def get_heatmap_data(db: Session):
    """Generate heatmap coordinates"""
    crimes = db.query(Crime.latitude, Crime.longitude).all()
    return [[c.latitude, c.longitude, 1.0] for c in crimes]
```

**Why separate service layer?**
- Keeps routes clean and focused on HTTP handling
- Business logic can be reused across multiple endpoints
- Easier to test independently
- Follows single responsibility principle

---

### 7. **services/prediction_service.py** - ARIMA Forecasting

**Purpose**: Predicts future crime trends using time-series analysis.

**ARIMA Model Explanation**:

ARIMA (AutoRegressive Integrated Moving Average) has 3 parameters:
- **p (AutoRegressive)**: Number of past values to use (we use p=1)
- **d (Integrated)**: Differencing to make data stationary (d=1)
- **q (Moving Average)**: Number of lagged forecast errors (q=1)

**Implementation**:

```python
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

def predict_crimes(db: Session, days_ahead: int):
    """Generate crime forecast using ARIMA"""
    
    # Step 1: Get historical data
    crimes = db.query(Crime).filter(
        Crime.occurred_at >= datetime.utcnow() - timedelta(days=90)
    ).all()
    
    # Step 2: Group by date
    df = pd.DataFrame([{
        'date': c.occurred_at.date(),
        'count': 1
    } for c in crimes])
    
    daily_crimes = df.groupby('date').size()
    
    # Step 3: Train ARIMA model
    model = ARIMA(daily_crimes, order=(1, 1, 1))
    fitted_model = model.fit()
    
    # Step 4: Forecast future
    forecast = fitted_model.forecast(steps=days_ahead)
    
    # Step 5: Get confidence intervals
    forecast_df = fitted_model.get_forecast(steps=days_ahead)
    confidence = forecast_df.conf_int()
    
    return {
        "forecast": forecast.tolist(),
        "dates": [str(date) for date in forecast.index],
        "lower_bound": confidence.iloc[:, 0].tolist(),
        "upper_bound": confidence.iloc[:, 1].tolist()
    }
```

**How it works**:
1. Retrieves 90 days of historical crime data
2. Groups crimes by date to create time series
3. Trains ARIMA(1,1,1) model on historical data
4. Generates forecast for next `days_ahead` days
5. Calculates confidence intervals (95% certainty bounds)

**Hotspot Detection**:

```python
from sklearn.cluster import DBSCAN
import numpy as np

def get_hotspots(db: Session):
    """Identify crime hotspots using DBSCAN clustering"""
    
    # Get recent crimes
    crimes = db.query(Crime).filter(
        Crime.occurred_at >= datetime.utcnow() - timedelta(days=30)
    ).all()
    
    # Extract coordinates
    coords = np.array([[c.latitude, c.longitude] for c in crimes])
    
    # Cluster nearby crimes
    clustering = DBSCAN(
        eps=0.01,  # ~1km radius
        min_samples=5  # Min 5 crimes to form cluster
    ).fit(coords)
    
    # Identify clusters
    labels = clustering.labels_
    hotspots = []
    
    for label in set(labels):
        if label == -1:  # Skip noise points
            continue
        
        # Get crimes in this cluster
        cluster_crimes = [c for i, c in enumerate(crimes) if labels[i] == label]
        
        # Calculate center
        avg_lat = sum(c.latitude for c in cluster_crimes) / len(cluster_crimes)
        avg_lng = sum(c.longitude for c in cluster_crimes) / len(cluster_crimes)
        
        hotspots.append({
            "latitude": avg_lat,
            "longitude": avg_lng,
            "crime_count": len(cluster_crimes),
            "risk_score": len(cluster_crimes) * 10,
            "severity": "high" if len(cluster_crimes) > 20 else "medium"
        })
    
    # Return top 10
    return sorted(hotspots, key=lambda x: x['risk_score'], reverse=True)[:10]
```

**DBSCAN Parameters**:
- `eps=0.01`: Maximum distance between points (~1km in lat/lng degrees)
- `min_samples=5`: Minimum crimes required to form a cluster

---

### 8. **services/route_service.py** - Safe Routing

**Purpose**: Calculates routes that avoid high-crime areas using OSRM.

**OSRM Integration**:

```python
import httpx

async def calculate_safe_route(db: Session, request: SafeRouteRequest):
    """Calculate safe route avoiding crime zones"""
    
    # Step 1: Get crime hotspots
    hotspots = get_hotspots(db)
    
    # Step 2: Call OSRM for road-based routing
    route_coords = await _get_route_from_osrm(
        request.start_lat, request.start_lng,
        request.end_lat, request.end_lng
    )
    
    # Step 3: Calculate route safety score
    safety_score = 100
    for coord in route_coords:
        for hotspot in hotspots:
            distance = haversine_distance(
                coord[0], coord[1],
                hotspot['latitude'], hotspot['longitude']
            )
            if distance < 0.5:  # Within 500m of hotspot
                safety_score -= 10
    
    safety_score = max(0, safety_score)
    
    # Step 4: Extract route metadata
    distance_km = sum(
        haversine_distance(route_coords[i][0], route_coords[i][1],
                          route_coords[i+1][0], route_coords[i+1][1])
        for i in range(len(route_coords) - 1)
    )
    
    return SafeRouteResponse(
        route=[[lat, lng] for lng, lat in route_coords],  # Swap for Leaflet
        distance_km=round(distance_km, 2),
        duration_minutes=int(distance_km * 5),  # Estimate 5 min/km
        safety_score=safety_score
    )

async def _get_route_from_osrm(start_lat, start_lng, end_lat, end_lng):
    """Get route from OSRM API"""
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}"
    params = {
        "overview": "full",
        "geometries": "geojson"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        # Extract coordinate array (200+ points for real roads)
        return data['routes'][0]['geometry']['coordinates']
```

**How it works**:
1. Identifies crime hotspots using clustering
2. Calls OSRM API to get road-based route (returns 200+ coordinate points)
3. Checks each route point against hotspots
4. Reduces safety score for points near crime zones
5. Returns route with safety score, distance, and estimated duration

**Why OSRM?**
- Free and open-source
- No API key required
- Returns real road-based routes (not straight lines)
- Fast response times
- Self-hostable for production

---

### 9. **services/chatbot_service.py** - AI Assistant

**Purpose**: Provides conversational responses to crime-related questions.

```python
def get_chatbot_response(message: str, db: Session):
    """Generate chatbot response"""
    message_lower = message.lower()
    
    # Keyword matching
    if any(word in message_lower for word in ['report', 'submit', 'how to report']):
        return {
            "response": "To report a crime, click the 'Report Crime' button at the top...",
            "data": None
        }
    
    elif any(word in message_lower for word in ['safe', 'route', 'navigation']):
        return {
            "response": "Use the Safe Routes tab to plan a route that avoids high-crime areas...",
            "data": None
        }
    
    elif any(word in message_lower for word in ['statistics', 'stats', 'numbers']):
        stats = crime_service.get_crime_stats(db, days=30)
        return {
            "response": f"In the last 30 days, there were {stats['total']} crimes reported...",
            "data": stats
        }
    
    else:
        return {
            "response": "I can help you with: reporting crimes, finding safe routes, crime statistics...",
            "data": None
        }
```

**Simple keyword-based chatbot**:
- Matches user message against predefined patterns
- Returns relevant information from database
- Can be upgraded to use NLP models (BERT, GPT) for better understanding

---

### 10. **scripts/ingest_data.py** - Synthetic Data

**Purpose**: Generates realistic synthetic crime data for testing and demo.

```python
def generate_synthetic_data(n_crimes: int = 1000):
    """Generate n synthetic crime records"""
    
    crimes = []
    crime_types = ['theft', 'assault', 'robbery', 'burglary', 'battery', ...]
    
    for _ in range(n_crimes):
        # Random crime type
        crime_type = random.choice(crime_types)
        
        # Random location (70% Hyderabad, 30% Chicago)
        if random.random() < 0.7:
            lat = random.uniform(17.3, 17.6)  # Hyderabad
            lng = random.uniform(78.3, 78.7)
        else:
            lat = random.uniform(41.7, 42.0)  # Chicago
            lng = random.uniform(-87.8, -87.5)
        
        # Random date (last 90 days)
        days_ago = random.randint(0, 90)
        occurred_at = datetime.utcnow() - timedelta(days=days_ago)
        
        # Random severity (weighted towards lower severity)
        severity = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        
        crimes.append(Crime(
            crime_type=crime_type,
            latitude=lat,
            longitude=lng,
            occurred_at=occurred_at,
            severity=severity,
            description=f"Synthetic {crime_type} incident",
            status="confirmed"
        ))
    
    return crimes
```

**Called automatically on startup** if database is empty.

---

## 🔄 Request Flow Example

**Example: User submits crime report**

1. **Frontend**: `POST /api/reports/` with JSON body
   ```json
   {
     "crime_type": "theft",
     "latitude": 17.4485,
     "longitude": 78.3908,
     "description": "Phone stolen at bus stop",
     "severity": 2,
     "location_description": "Madhapur"
   }
   ```

2. **routes.py**: Receives request
   ```python
   @reports_router.post("/", response_model=schemas.ReportResponse)
   def create_report(report: schemas.CrimeReportCreate, db: Session = Depends(get_db)):
       # Pydantic validates request automatically
       new_report = crime_service.create_crime_report(db, report)
       return new_report
   ```

3. **crime_service.py**: Business logic
   ```python
   def create_crime_report(db: Session, report: schemas.CrimeReportCreate):
       new_crime = Crime(
           crime_type=report.crime_type,
           latitude=report.latitude,
           longitude=report.longitude,
           description=report.description,
           severity=report.severity,
           location_description=report.location_description,
           status="pending",  # Requires moderation
           occurred_at=datetime.utcnow()
       )
       db.add(new_crime)
       db.commit()
       db.refresh(new_crime)
       return new_crime
   ```

4. **Response**: Returns JSON
   ```json
   {
     "id": 1001,
     "crime_type": "theft",
     "latitude": 17.4485,
     "longitude": 78.3908,
     "occurred_at": "2026-01-17T10:30:00",
     "severity": 2,
     "description": "Phone stolen at bus stop",
     "status": "pending"
   }
   ```

5. **WebSocket**: Broadcasts to all connected clients
   ```python
   await broadcast_to_websockets(new_crime)
   ```

---

## 🚀 Running the Backend

### Development
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Render)
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Environment: `DATABASE_URL=postgresql://...` (optional)

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📦 Dependencies

**Key packages**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `pydantic` - Data validation
- `statsmodels` - ARIMA forecasting
- `scikit-learn` - Clustering
- `pandas` - Data manipulation
- `httpx` - Async HTTP client

See `requirements.txt` for full list.

---

## 🔐 Security Notes

- API keys stored in environment variables (never hardcoded)
- CORS configured for specific origins in production
- SQL injection prevented by SQLAlchemy ORM
- Input validation via Pydantic schemas
- Rate limiting recommended for production

---

## 📚 Further Reading

- FastAPI docs: https://fastapi.tiangolo.com/
- SQLAlchemy docs: https://docs.sqlalchemy.org/
- ARIMA tutorial: https://www.statsmodels.org/stable/generated/statsmodels.tsa.arima.model.ARIMA.html
- DBSCAN clustering: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html

---

**For questions or issues, open a GitHub issue.**
