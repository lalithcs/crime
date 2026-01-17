# Frontend - CrimeScope React Application

This folder contains the React frontend that provides an intuitive user interface for crime visualization, reporting, and safety planning.

---

## 📁 Folder Structure

```
frontend/
├── public/
│   └── index.html               # HTML entry point
├── src/
│   ├── index.js                 # React app entry point
│   ├── App.jsx                  # Main application component
│   ├── App.css                  # Global styles
│   ├── components/
│   │   ├── CrimeMap.jsx         # Interactive Leaflet map
│   │   ├── CrimeMap.css
│   │   ├── Dashboard.jsx        # Analytics dashboard
│   │   ├── Dashboard.css
│   │   ├── ReportForm.jsx       # Crime reporting form
│   │   ├── ReportForm.css
│   │   ├── RoutePlanner.jsx     # Safe route planner
│   │   ├── RoutePlanner.css
│   │   ├── Chatbot.jsx          # AI assistant
│   │   ├── Chatbot.css
│   │   ├── AlertsPanel.jsx      # Real-time alerts sidebar
│   │   └── AlertsPanel.css
│   ├── services/
│   │   └── api.js               # Axios API client
│   └── constants/
│       └── locations.js         # 55 predefined locations
├── package.json                 # Node.js dependencies
└── README.md                    # This file
```

---

## 🎨 Component Overview

### 1. **App.jsx** - Main Application Shell

**Purpose**: Root component that manages navigation, layout, and global state.

**Key Features**:
- Tab-based navigation (Live Map, Safe Routes, Chat)
- Manages active view state
- Controls modal visibility (Report Form)
- Integrates Alerts Panel (always visible sidebar)
- Global toast notifications

**Code Structure**:

```jsx
function App() {
  const [activeTab, setActiveTab] = useState('map');  // Current view
  const [showReportForm, setShowReportForm] = useState(false);  // Modal state
  const [showChatbot, setShowChatbot] = useState(false);

  return (
    <div className="app">
      {/* Header with logo and Report Crime button */}
      <header className="app-header">
        <div className="logo">
          <Activity size={28} />
          <h1>CrimeScope</h1>
        </div>
        <button onClick={() => setShowReportForm(true)}>
          Report Crime
        </button>
      </header>

      {/* Tab Navigation */}
      <nav className="main-nav">
        <button 
          className={activeTab === 'map' ? 'active' : ''}
          onClick={() => setActiveTab('map')}
        >
          <Map size={20} /> Live Map
        </button>
        <button 
          className={activeTab === 'routes' ? 'active' : ''}
          onClick={() => setActiveTab('routes')}
        >
          <Route size={20} /> Safe Routes
        </button>
        <button 
          onClick={() => setShowChatbot(true)}
        >
          <MessageSquare size={20} /> Chat
        </button>
      </nav>

      {/* Main Content Area */}
      <div className="app-content">
        {activeTab === 'map' && <CrimeMap />}
        {activeTab === 'routes' && <RoutePlanner />}
        
        {/* Alerts Panel - Always visible on right side */}
        <AlertsPanel />
      </div>

      {/* Modals */}
      {showReportForm && <ReportForm onClose={() => setShowReportForm(false)} />}
      {showChatbot && <Chatbot onClose={() => setShowChatbot(false)} />}
      
      {/* Global toast notifications */}
      <Toaster position="top-right" />
    </div>
  );
}
```

**State Management**:
- `activeTab`: Controls which main component is displayed
- `showReportForm`: Toggles crime reporting modal
- `showChatbot`: Toggles chatbot modal
- Uses React hooks (`useState`) for state management

---

### 2. **CrimeMap.jsx** - Interactive Crime Visualization

**Purpose**: Displays crimes on an interactive Leaflet map with real-time updates.

**Key Features**:
- Interactive map centered on Hyderabad (17.385°N, 78.486°E)
- Crime markers (red) and user report markers (blue)
- Environmental factor markers (yellow circles)
- WebSocket connection for real-time updates
- Filters (crime type, date range, toggle reports/factors)
- Click markers to see crime details in popup

**Core Logic**:

```jsx
function CrimeMap() {
  const [crimes, setCrimes] = useState([]);
  const [userReports, setUserReports] = useState([]);
  const [environmentalFactors, setEnvironmentalFactors] = useState([]);
  const [filters, setFilters] = useState({
    showCrimes: true,
    showReports: true,
    showFactors: true,
    crimeType: '',
    days: 30
  });

  // Load data on mount and when filters change
  useEffect(() => {
    loadData();
  }, [filters.crimeType, filters.days]);

  const loadData = async () => {
    try {
      const [crimesRes, reportsRes, factorsRes] = await Promise.all([
        crimesAPI.getCrimes({ 
          crime_type: filters.crimeType || undefined,
          days: filters.days,
          limit: 500 
        }),
        reportsAPI.getReports(),
        causesAPI.getFactors()
      ]);
      
      setCrimes(crimesRes.data || []);
      setUserReports(reportsRes.data || []);
      setEnvironmentalFactors(factorsRes.data || []);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load crime data');
    }
  };

  return (
    <div className="crime-map-container">
      {/* Filter Controls */}
      <div className="map-controls">
        <select 
          value={filters.crimeType}
          onChange={(e) => setFilters({...filters, crimeType: e.target.value})}
        >
          <option value="">All Crime Types</option>
          <option value="theft">Theft</option>
          <option value="assault">Assault</option>
          {/* ... more options */}
        </select>
        
        <label>
          <input 
            type="checkbox"
            checked={filters.showCrimes}
            onChange={(e) => setFilters({...filters, showCrimes: e.target.checked})}
          />
          Show Crimes ({crimes.length})
        </label>
        
        {/* ... more controls */}
      </div>

      {/* Leaflet Map */}
      <MapContainer 
        center={[17.385, 78.486]}  // Hyderabad coordinates
        zoom={12}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        
        {/* WebSocket handler for real-time updates */}
        <WebSocketHandler onNewReport={(report) => {
          setUserReports(prev => [report, ...prev]);
          toast.success('New crime report received!');
        }} />
        
        {/* Crime Markers */}
        {filters.showCrimes && crimes.map((crime) => (
          <Marker 
            key={crime.id}
            position={[crime.latitude, crime.longitude]}
            icon={crimeIcon}
          >
            <Popup>
              <strong>{crime.crime_type.toUpperCase()}</strong>
              <br />
              {crime.location_description}
              <br />
              <small>{new Date(crime.occurred_at).toLocaleDateString()}</small>
              <br />
              {crime.description}
            </Popup>
          </Marker>
        ))}
        
        {/* User Report Markers */}
        {filters.showReports && userReports.map((report) => (
          <Marker 
            key={report.id}
            position={[report.latitude, report.longitude]}
            icon={reportIcon}
          >
            <Popup>
              <strong>User Report: {report.crime_type}</strong>
              <br />
              Status: {report.status}
              <br />
              {report.description}
            </Popup>
          </Marker>
        ))}
        
        {/* Environmental Factor Circles */}
        {filters.showFactors && environmentalFactors.map((factor) => (
          <Circle
            key={factor.id}
            center={[factor.latitude, factor.longitude]}
            radius={200}  // 200m radius
            pathOptions={{ color: 'yellow', fillColor: 'yellow', fillOpacity: 0.3 }}
          >
            <Popup>
              <strong>{factor.factor_type}</strong>
              <br />
              {factor.description}
            </Popup>
          </Circle>
        ))}
      </MapContainer>
    </div>
  );
}
```

**WebSocket Handler**:

```jsx
function WebSocketHandler({ onNewReport }) {
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect to backend WebSocket
    const wsUrl = process.env.REACT_APP_API_URL 
      ? process.env.REACT_APP_API_URL.replace('https://', 'wss://').replace('http://', 'ws://') + '/ws/live'
      : 'ws://localhost:8000/ws/live';
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => console.log('WebSocket connected');
    
    ws.onmessage = (event) => {
      const newReport = JSON.parse(event.data);
      onNewReport(newReport);  // Update parent state
    };
    
    ws.onerror = (error) => console.error('WebSocket error:', error);
    
    ws.onclose = () => console.log('WebSocket disconnected');
    
    wsRef.current = ws;
    
    // Cleanup on unmount
    return () => ws.close();
  }, []);

  return null;  // This component doesn't render anything
}
```

**Custom Marker Icons**:

```jsx
const crimeIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="25" height="41" viewBox="0 0 25 41">
      <path fill="#e53e3e" d="M12.5 0C5.6 0 0 5.6 0 12.5c0 8.4 12.5 28.5 12.5 28.5S25 20.9 25 12.5C25 5.6 19.4 0 12.5 0z"/>
      <circle fill="white" cx="12.5" cy="12.5" r="6"/>
    </svg>
  `),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});
```

---

### 3. **Dashboard.jsx** - Analytics & Charts

**Purpose**: Displays crime statistics, trends, and visualizations.

**Key Features**:
- Crime count by type (bar chart)
- Time-series trend chart (line chart)
- Top 10 hotspots table
- Crime severity distribution (pie chart)
- Safety score by location

**Implementation**:

```jsx
import { BarChart, Bar, LineChart, Line, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [hotspots, setHotspots] = useState([]);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    const statsRes = await crimesAPI.getStats(30);
    const hotspotsRes = await predictionsAPI.getHotspots(7);
    
    setStats(statsRes.data);
    setHotspots(hotspotsRes.data.hotspots);
  };

  // Transform data for charts
  const crimesByType = Object.entries(stats?.by_type || {}).map(([type, count]) => ({
    type,
    count
  }));

  return (
    <div className="dashboard">
      <h2>Crime Analytics Dashboard</h2>
      
      {/* Summary Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>{stats?.total || 0}</h3>
          <p>Total Crimes (30 days)</p>
        </div>
        <div className="stat-card">
          <h3>{stats?.avg_per_day?.toFixed(1) || 0}</h3>
          <p>Crimes Per Day</p>
        </div>
        <div className="stat-card">
          <h3>{hotspots.length}</h3>
          <p>Active Hotspots</p>
        </div>
      </div>

      {/* Crime Types Bar Chart */}
      <div className="chart-container">
        <h3>Crimes by Type</h3>
        <BarChart width={600} height={300} data={crimesByType}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="type" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#e53e3e" />
        </BarChart>
      </div>

      {/* Hotspots Table */}
      <div className="hotspots-table">
        <h3>Top 10 Crime Hotspots</h3>
        <table>
          <thead>
            <tr>
              <th>Location</th>
              <th>Crime Count</th>
              <th>Risk Score</th>
              <th>Severity</th>
            </tr>
          </thead>
          <tbody>
            {hotspots.map((hotspot, idx) => (
              <tr key={idx}>
                <td>{hotspot.location}</td>
                <td>{hotspot.crime_count}</td>
                <td>{hotspot.risk_score}</td>
                <td>
                  <span className={`severity-badge ${hotspot.severity}`}>
                    {hotspot.severity}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

### 4. **ReportForm.jsx** - Crime Reporting

**Purpose**: Modal form for citizens to submit crime reports.

**Key Features**:
- Crime type dropdown (10+ types)
- Location dropdown (55 predefined locations)
- Description textarea
- Severity slider (1-3)
- Optional photo upload
- GPS "Use Current Location" button

**Implementation**:

```jsx
function ReportForm({ onClose }) {
  const [selectedLocation, setSelectedLocation] = useState(ALL_LOCATIONS[0].name);
  const [formData, setFormData] = useState({
    crime_type: 'theft',
    description: '',
    severity: 2
  });

  const handleLocationChange = (locationName) => {
    const location = ALL_LOCATIONS.find(loc => loc.name === locationName);
    if (location) {
      setSelectedLocation(locationName);
      setFormData(prev => ({
        ...prev,
        latitude: location.lat,
        longitude: location.lng,
        location_description: locationName
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const location = ALL_LOCATIONS.find(loc => loc.name === selectedLocation);
      
      const reportData = {
        crime_type: formData.crime_type,
        latitude: location.lat,
        longitude: location.lng,
        description: formData.description,
        severity: formData.severity,
        location_description: selectedLocation
      };
      
      await reportsAPI.createReport(reportData);
      toast.success('Crime report submitted successfully!');
      onClose();
    } catch (error) {
      toast.error('Failed to submit report. Please try again.');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Report a Crime</h2>
          <button onClick={onClose}><X size={24} /></button>
        </div>
        
        <form onSubmit={handleSubmit}>
          {/* Crime Type */}
          <div className="form-group">
            <label>Crime Type *</label>
            <select 
              value={formData.crime_type}
              onChange={(e) => setFormData({...formData, crime_type: e.target.value})}
              required
            >
              <option value="theft">Theft</option>
              <option value="assault">Assault</option>
              <option value="robbery">Robbery</option>
              <option value="burglary">Burglary</option>
              {/* ... more options */}
            </select>
          </div>
          
          {/* Location Dropdown */}
          <div className="form-group">
            <label>Location *</label>
            <select 
              value={selectedLocation}
              onChange={(e) => handleLocationChange(e.target.value)}
              required
            >
              {ALL_LOCATIONS.map(loc => (
                <option key={loc.name} value={loc.name}>
                  {loc.name} ({loc.city})
                </option>
              ))}
            </select>
          </div>
          
          {/* Description */}
          <div className="form-group">
            <label>Description *</label>
            <textarea 
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Please describe what happened..."
              rows={4}
              required
            />
          </div>
          
          {/* Severity */}
          <div className="form-group">
            <label>Severity: {formData.severity}</label>
            <input 
              type="range"
              min="1"
              max="3"
              value={formData.severity}
              onChange={(e) => setFormData({...formData, severity: parseInt(e.target.value)})}
            />
            <div className="severity-labels">
              <span>Low</span>
              <span>Medium</span>
              <span>High</span>
            </div>
          </div>
          
          <button type="submit" className="btn-primary">
            Submit Report
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

### 5. **RoutePlanner.jsx** - Safe Route Calculation

**Purpose**: Plans routes that avoid high-crime areas.

**Key Features**:
- Start/end location dropdowns (55 locations)
- "Use Current Location" buttons for GPS
- Calculate safe route button
- Displays route on mini-map
- Shows distance, duration, and safety score

**Implementation**:

```jsx
function RoutePlanner() {
  const [selectedStartLocation, setSelectedStartLocation] = useState(ALL_LOCATIONS[2].name);
  const [selectedEndLocation, setSelectedEndLocation] = useState(ALL_LOCATIONS[0].name);
  const [route, setRoute] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLocationChange = (type, locationName) => {
    const location = ALL_LOCATIONS.find(loc => loc.name === locationName);
    if (!location) return;
    
    if (type === 'start') {
      setSelectedStartLocation(locationName);
    } else {
      setSelectedEndLocation(locationName);
    }
  };

  const handleCalculateRoute = async () => {
    setLoading(true);
    
    try {
      const start = ALL_LOCATIONS.find(loc => loc.name === selectedStartLocation);
      const end = ALL_LOCATIONS.find(loc => loc.name === selectedEndLocation);
      
      const response = await routesAPI.getSafeRoute({
        start_lat: start.lat,
        start_lng: start.lng,
        end_lat: end.lat,
        end_lng: end.lng
      });
      
      setRoute(response.data);
      toast.success('Safe route calculated!');
    } catch (error) {
      toast.error('Failed to calculate route');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="route-planner">
      <div className="route-form">
        <h2>🛣️ Safe Route Planner</h2>
        
        {/* Start Location */}
        <div className="form-group">
          <label>Start Location</label>
          <select 
            value={selectedStartLocation}
            onChange={(e) => handleLocationChange('start', e.target.value)}
          >
            {ALL_LOCATIONS.map(loc => (
              <option key={loc.name} value={loc.name}>
                {loc.name}
              </option>
            ))}
          </select>
        </div>
        
        {/* End Location */}
        <div className="form-group">
          <label>End Location</label>
          <select 
            value={selectedEndLocation}
            onChange={(e) => handleLocationChange('end', e.target.value)}
          >
            {ALL_LOCATIONS.map(loc => (
              <option key={loc.name} value={loc.name}>
                {loc.name}
              </option>
            ))}
          </select>
        </div>
        
        <button 
          onClick={handleCalculateRoute}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Calculating...' : 'Calculate Safe Route'}
        </button>
        
        {/* Route Info */}
        {route && (
          <div className="route-info">
            <h3>Route Details</h3>
            <div className="route-stats">
              <div className="stat">
                <strong>Distance:</strong> {route.distance_km} km
              </div>
              <div className="stat">
                <strong>Duration:</strong> {route.duration_minutes} min
              </div>
              <div className="stat">
                <strong>Safety Score:</strong>
                <span className={`score ${route.safety_score > 70 ? 'safe' : route.safety_score > 40 ? 'moderate' : 'danger'}`}>
                  {route.safety_score}/100
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Route Map */}
      {route && (
        <MapContainer center={route.route[0]} zoom={13} style={{ height: '500px' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Polyline 
            positions={route.route}  // Array of [lat, lng] points
            color={route.safety_score > 70 ? 'green' : route.safety_score > 40 ? 'orange' : 'red'}
            weight={5}
          />
          <Marker position={route.route[0]} />  {/* Start marker */}
          <Marker position={route.route[route.route.length - 1]} />  {/* End marker */}
        </MapContainer>
      )}
    </div>
  );
}
```

---

### 6. **Chatbot.jsx** - AI Assistant

**Purpose**: Provides instant answers to crime-related questions.

**Key Features**:
- 10 pre-loaded FAQs
- Show/hide FAQ section
- Chat message history
- Scrollable message area

**Implementation**:

```jsx
function Chatbot({ onClose }) {
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Hello! I\'m your crime information assistant. Ask me anything or select a question below!', timestamp: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [showFAQ, setShowFAQ] = useState(true);

  const faqs = [
    { q: 'How do I report a crime?', a: 'Click the "Report Crime" button at the top, select the crime type, choose your location from the dropdown, and submit.' },
    { q: 'How can I find a safe route?', a: 'Go to the "Safe Routes" tab, select your start and end locations, and click "Calculate Safe Route".' },
    { q: 'What are crime predictions?', a: 'Crime predictions show areas where crimes are likely to occur based on historical patterns.' },
    // ... 7 more FAQs
  ];

  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Add user message
    const userMessage = { type: 'user', text: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    
    try {
      // Get bot response from API
      const response = await chatbotAPI.chat({ message: input });
      const botMessage = { type: 'bot', text: response.data.response, timestamp: new Date() };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = { type: 'bot', text: 'Sorry, I encountered an error.', timestamp: new Date() };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleFAQClick = (faq) => {
    const userMessage = { type: 'user', text: faq.q, timestamp: new Date() };
    const botMessage = { type: 'bot', text: faq.a, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage, botMessage]);
  };

  return (
    <div className="chatbot-overlay">
      <div className="chatbot-container">
        <div className="chatbot-header">
          <h2>💬 Crime Assistant</h2>
          <button onClick={onClose}><X /></button>
        </div>
        
        <div className="chatbot-messages">
          {/* Chat History */}
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.type}`}>
              <div className="message-content">{msg.text}</div>
              <div className="message-time">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))}
          
          {/* FAQ Section */}
          {showFAQ && (
            <div className="faq-section">
              <h3>Frequently Asked Questions</h3>
              {faqs.map((faq, idx) => (
                <button 
                  key={idx}
                  className="faq-btn"
                  onClick={() => handleFAQClick(faq)}
                >
                  {faq.q}
                </button>
              ))}
              <button 
                className="hide-faq-btn"
                onClick={() => setShowFAQ(false)}
              >
                Hide FAQs
              </button>
            </div>
          )}
          
          {!showFAQ && (
            <button 
              className="show-faq-btn"
              onClick={() => setShowFAQ(true)}
            >
              Show FAQs
            </button>
          )}
        </div>
        
        {/* Input Area */}
        <div className="chatbot-input">
          <input 
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask me about crime safety..."
          />
          <button onClick={handleSend}><Send size={20} /></button>
        </div>
      </div>
    </div>
  );
}
```

---

### 7. **AlertsPanel.jsx** - Real-time Alerts

**Purpose**: Sidebar showing recent crime alerts.

**Key Features**:
- Auto-refreshes every 30 seconds
- Shows most recent 10 alerts
- Color-coded by severity
- Time ago display (e.g., "5 minutes ago")

**Implementation**:

```jsx
function AlertsPanel() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 30000);  // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadAlerts = async () => {
    try {
      const response = await alertsAPI.getAlerts(10);
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Failed to load alerts');
    }
  };

  const getTimeAgo = (date) => {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  return (
    <div className="alerts-panel">
      <h3>🚨 Community Alerts</h3>
      <div className="alerts-list">
        {alerts.map(alert => (
          <div key={alert.id} className={`alert-item severity-${alert.severity}`}>
            <div className="alert-type">{alert.crime_type}</div>
            <div className="alert-location">{alert.location}</div>
            <div className="alert-time">{getTimeAgo(alert.occurred_at)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔌 API Integration

### **api.js** - Centralized API Client

**Purpose**: Provides axios-based functions for all backend endpoints.

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL 
  ? `${process.env.REACT_APP_API_URL}/api`
  : 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Crimes API
export const crimesAPI = {
  getCrimes: (params) => api.get('/crimes/', { params }),
  getStats: (days = 30) => api.get('/crimes/stats', { params: { days } }),
  getHeatmap: (params) => api.get('/crimes/heatmap', { params }),
};

// Reports API
export const reportsAPI = {
  createReport: (data) => api.post('/reports/', data),
  getReports: (params) => api.get('/reports/', { params }),
};

// Predictions API
export const predictionsAPI = {
  predict: (data) => api.post('/predictions/', data),
  getHotspots: (days = 7) => api.get('/predictions/hotspots', { params: { days_ahead: days } }),
};

// Routes API
export const routesAPI = {
  getSafeRoute: (data) => api.post('/routes/safe', data),
};

// Chatbot API
export const chatbotAPI = {
  chat: (data) => api.post('/chatbot/', data),
};

// Alerts API
export const alertsAPI = {
  getAlerts: (limit = 10) => api.get('/alerts/', { params: { limit } }),
};

// Causes API (Environmental Factors)
export const causesAPI = {
  getFactors: () => api.get('/causes/'),
};
```

**Usage in components**:
```javascript
import { crimesAPI } from '../services/api';

const fetchCrimes = async () => {
  const response = await crimesAPI.getCrimes({ crime_type: 'theft', days: 30 });
  console.log(response.data);  // Array of crime objects
};
```

---

## 📍 Location Constants

### **constants/locations.js**

**Purpose**: Centralized location database for dropdowns.

```javascript
export const HYDERABAD_LOCATIONS = [
  { name: "Madhapur", lat: 17.4485, lng: 78.3908 },
  { name: "Gachibowli", lat: 17.4400, lng: 78.3487 },
  { name: "Malkajgiri", lat: 17.4474, lng: 78.5268 },
  { name: "Medchal", lat: 17.6282, lng: 78.4814 },
  // ... 41 more Hyderabad locations
];

export const CHICAGO_LOCATIONS = [
  { name: "The Loop", lat: 41.8781, lng: -87.6298 },
  { name: "Lincoln Park", lat: 41.9210, lng: -87.6532 },
  // ... 8 more Chicago locations
];

export const ALL_LOCATIONS = [
  ...HYDERABAD_LOCATIONS.map(loc => ({ ...loc, city: "Hyderabad" })),
  ...CHICAGO_LOCATIONS.map(loc => ({ ...loc, city: "Chicago" })),
];
```

**Total**: 45 Hyderabad + 10 Chicago = **55 locations**

---

## 🎨 Styling

**Global styles** in `App.css`:
- CSS variables for theming
- Flexbox layouts
- Responsive design (works on mobile/tablet)
- Dark mode compatible

**Component styles**:
- Each component has its own CSS file
- BEM naming convention
- Modular and maintainable

---

## 🚀 Running the Frontend

### Development
```bash
cd frontend
npm install
npm start
```
Opens at: `http://localhost:3000`

### Production Build
```bash
npm run build
```
Creates optimized build in `build/` folder

### Deploy to Vercel
1. Connect GitHub repo
2. Set `REACT_APP_API_URL=https://your-backend.com`
3. Auto-deploys on push

---

## 📦 Dependencies

**Key packages**:
- `react` - UI library
- `react-leaflet` - Map components
- `axios` - HTTP client
- `recharts` - Charts
- `lucide-react` - Icons
- `react-hot-toast` - Notifications

See `package.json` for full list.

---

## 🔐 Environment Variables

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000
```

**Production**:
```env
REACT_APP_API_URL=https://crimebackend-uhts.onrender.com
```

---

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

**For questions, open a GitHub issue.**
