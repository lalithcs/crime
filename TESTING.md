# Testing Guide

## Running Tests

### Backend Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_crimes.py

# Run specific test
pytest tests/test_crimes.py::test_create_crime_report
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Manual Testing Checklist

### 1. Real-time Dashboard & Map ✓

- [ ] Map loads correctly
- [ ] Crime markers appear on map
- [ ] User reports appear on map
- [ ] Environmental factors display correctly
- [ ] WebSocket connection establishes
- [ ] Real-time updates work
- [ ] Map filters work (crimes, reports, factors)
- [ ] Popup information displays correctly

**Test Steps:**
1. Open http://localhost:3000
2. Navigate to "Live Map" tab
3. Verify crime markers (red) and report markers (blue)
4. Click on markers to see details
5. Toggle filters on/off
6. Submit a new report and verify it appears immediately

### 2. User Crime Reporting ✓

- [ ] Report form opens
- [ ] All form fields work
- [ ] Location picker works
- [ ] Form validation works
- [ ] Submission successful
- [ ] New report appears on map
- [ ] Toast notification shows

**Test Steps:**
1. Click "Report Crime" button
2. Fill in crime type, description
3. Click "Use My Current Location" (or enter manually)
4. Submit form
5. Verify toast success message
6. Check map for new blue marker

### 3. ARIMA Crime Prediction ✓

- [ ] Dashboard shows predictions
- [ ] Prediction chart displays correctly
- [ ] Forecast data is reasonable
- [ ] Confidence intervals show
- [ ] Model accuracy displays
- [ ] Hotspots show on dashboard

**Test Steps:**
1. Navigate to "Dashboard" tab
2. Verify "7-Day Crime Forecast" chart
3. Check prediction values are > 0
4. Verify confidence interval lines
5. Scroll to "Predicted Crime Hotspots" table
6. Verify severity badges

### 4. Community Alert Engine ✓

- [ ] Alerts panel displays
- [ ] Active alerts load
- [ ] Alert severity colors correct
- [ ] Can minimize/expand alerts panel
- [ ] Real-time alert notifications
- [ ] Alert badge shows count

**Test Steps:**
1. Look for alerts panel in top-right
2. Verify alert count badge
3. Click alerts to view details
4. Test minimize button
5. Submit test alert via API and check real-time update

### 5. Safety Route Planner ✓

- [ ] Route form works
- [ ] Start/end location inputs work
- [ ] "Use Current Location" works
- [ ] Route calculation successful
- [ ] Route displays on map
- [ ] Route details show (distance, time, safety score)
- [ ] Avoided crime zones count
- [ ] Route comparison works

**Test Steps:**
1. Navigate to "Safe Routes" tab
2. Enter start location (e.g., 41.8781, -87.6298)
3. Enter end location (e.g., 41.9, -87.65)
4. Click "Calculate Safe Route"
5. Verify route line appears on map
6. Check route details panel shows correct info
7. Click "Compare Routes" to see comparison

**Critical Fix Applied:**
- ✅ Route calculation now uses proper avoidance algorithm
- ✅ Waypoints added to avoid crime zones
- ✅ Direction is calculated correctly (not reversed)
- ✅ Safety score reflects actual risk avoidance

### 6. Sentiment Analysis (NLP) ✓

- [ ] Sentiment form works
- [ ] Text analysis successful
- [ ] Sentiment (positive/negative/neutral) correct
- [ ] Sentiment score displays
- [ ] Confidence level shows
- [ ] Trends chart updates
- [ ] Distribution chart works

**Test Steps:**
1. Navigate to "Sentiment" tab
2. Enter text: "I feel very safe in this neighborhood"
3. Click "Analyze Sentiment"
4. Verify result shows POSITIVE with score
5. Enter negative text: "Crime is terrible here, very unsafe"
6. Verify result shows NEGATIVE
7. Check trends section updates

### 7. Crime Chatbot ✓

- [ ] Chatbot opens
- [ ] Quick questions display
- [ ] Can send messages
- [ ] Bot responds correctly
- [ ] Typing indicator shows
- [ ] Chat history maintained
- [ ] Bot answers crime stats
- [ ] Bot provides predictions
- [ ] Bot gives safety tips

**Test Steps:**
1. Click floating chatbot button (bottom-right)
2. Try quick question: "Show me crime statistics"
3. Verify bot response with stats
4. Ask: "What are the crime predictions?"
5. Ask: "Give me safety tips"
6. Ask: "How do I report a crime?"
7. Verify all responses are relevant

### 8. Crime Cause Mapper ✓

- [ ] Environmental factors load on map
- [ ] Factors have correct icons
- [ ] Factors have severity colors
- [ ] Can view factor details
- [ ] Circles show risk areas
- [ ] Filter works for factors

**Test Steps:**
1. Go to "Live Map"
2. Ensure "Show Factors" is checked
3. Look for circles on map (colored zones)
4. Click on factor markers
5. Verify popup shows:
   - Factor type (poor lighting, construction, etc.)
   - Severity
   - Description

## API Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get crimes
curl http://localhost:8000/api/crimes/

# Get crime stats
curl http://localhost:8000/api/crimes/stats?days=30

# Submit crime report
curl -X POST http://localhost:8000/api/reports/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "crime_type": "THEFT",
    "description": "Test report",
    "latitude": 41.8781,
    "longitude": -87.6298,
    "location_description": "Street corner"
  }'

# Get predictions
curl -X POST http://localhost:8000/api/predictions/ \
  -H "Content-Type: application/json" \
  -d '{
    "days_ahead": 7
  }'

# Calculate safe route
curl -X POST http://localhost:8000/api/routes/safe \
  -H "Content-Type: application/json" \
  -d '{
    "start_lat": 41.8781,
    "start_lng": -87.6298,
    "end_lat": 41.9,
    "end_lng": -87.65,
    "avoid_crime_radius_km": 0.5
  }'

# Analyze sentiment
curl -X POST http://localhost:8000/api/sentiment/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I feel very safe in this neighborhood"
  }'

# Chat with bot
curl -X POST http://localhost:8000/api/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me crime statistics"
  }'

# Get alerts
curl http://localhost:8000/api/alerts/

# Get environmental factors
curl http://localhost:8000/api/causes/
```

### Using Postman/Insomnia

1. Import OpenAPI spec from http://localhost:8000/docs
2. Test all endpoints
3. Check response codes and data structure

## Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

## Performance Benchmarks

### Expected Response Times

- GET /api/crimes/: < 200ms
- POST /api/reports/: < 100ms
- POST /api/predictions/: < 3000ms (ARIMA calculation)
- POST /api/routes/safe: < 500ms
- POST /api/sentiment/: < 1000ms (NLP processing)
- GET /api/alerts/: < 100ms

### Expected Throughput

- 100+ requests/second for simple GET endpoints
- 50+ requests/second for POST endpoints
- WebSocket: 1000+ concurrent connections

## Browser Compatibility

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

## Mobile Responsive Testing

- [ ] Map displays correctly on mobile
- [ ] Forms are usable on mobile
- [ ] Navigation works on small screens
- [ ] Touch interactions work
- [ ] Chatbot works on mobile

## Security Testing

- [ ] SQL injection attempts fail
- [ ] XSS attempts are sanitized
- [ ] CORS properly configured
- [ ] No sensitive data in responses
- [ ] API rate limiting works

## Known Issues & Limitations

1. **Dataset**: Using synthetic data if Chicago API fails
2. **Routing**: Simple algorithm, not production-quality routing (use OpenRouteService for production)
3. **NLP**: Lightweight model, may need fine-tuning for domain-specific sentiment
4. **ARIMA**: Requires 30+ days of data for accurate predictions
5. **WebSocket**: Basic implementation, consider Socket.IO for production scale

## Test Coverage Goals

- Backend: > 80% code coverage
- Frontend: > 70% code coverage
- Critical paths: 100% coverage

## Continuous Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm test -- --coverage
```
