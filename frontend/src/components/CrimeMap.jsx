import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import { crimesAPI, reportsAPI, causesAPI } from '../services/api';
import toast from 'react-hot-toast';
import { AlertTriangle, Construction, Lightbulb } from 'lucide-react';
import './CrimeMap.css';

// Fix Leaflet default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom crime icons
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

const reportIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="25" height="41" viewBox="0 0 25 41">
      <path fill="#3182ce" d="M12.5 0C5.6 0 0 5.6 0 12.5c0 8.4 12.5 28.5 12.5 28.5S25 20.9 25 12.5C25 5.6 19.4 0 12.5 0z"/>
      <circle fill="white" cx="12.5" cy="12.5" r="6"/>
    </svg>
  `),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

function WebSocketHandler({ onNewReport }) {
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const wsUrl = process.env.REACT_APP_API_URL 
      ? process.env.REACT_APP_API_URL.replace('https://', 'wss://').replace('http://', 'ws://') + '/ws/live'
      : 'ws://localhost:8000/ws/live';
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected to:', wsUrl);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'new_report') {
        toast.success('New crime report added!');
        onNewReport(data.data);
      } else if (data.type === 'new_alert') {
        toast.error(`Alert: ${data.data.title}`, { duration: 5000 });
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [onNewReport]);

  return null;
}

function CrimeMap() {
  const [crimes, setCrimes] = useState([]);
  const [reports, setReports] = useState([]);
  const [environmentalFactors, setEnvironmentalFactors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    showCrimes: true,
    showReports: true,
    showFactors: true,
    crimeType: '',
    days: 30,
  });
  const [center] = useState([17.385, 78.486]); // Hyderabad, India

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.crimeType, filters.days]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [crimesRes, reportsRes, factorsRes] = await Promise.all([
        crimesAPI.getCrimes({ 
          limit: 500, 
          crime_type: filters.crimeType || undefined 
        }),
        reportsAPI.getReports({ limit: 100 }),
        causesAPI.getFactors({ resolved: false }),
      ]);

      setCrimes(crimesRes.data || []);
      setReports(reportsRes.data || []);
      setEnvironmentalFactors(factorsRes.data || []);
    } catch (error) {
      console.error('Error loading map data:', error);
      toast.error('Failed to load map data');
    } finally {
      setLoading(false);
    }
  };

  const handleNewReport = (newReport) => {
    setReports(prev => [newReport, ...prev]);
  };

  return (
    <div className="crime-map-container">
      <div className="map-controls">
        <div className="filter-group">
          <label>
            <input
              type="checkbox"
              checked={filters.showCrimes}
              onChange={(e) => setFilters({ ...filters, showCrimes: e.target.checked })}
            />
            Show Crimes ({crimes.length})
          </label>
          <label>
            <input
              type="checkbox"
              checked={filters.showReports}
              onChange={(e) => setFilters({ ...filters, showReports: e.target.checked })}
            />
            Show Reports ({reports.length})
          </label>
          <label>
            <input
              type="checkbox"
              checked={filters.showFactors}
              onChange={(e) => setFilters({ ...filters, showFactors: e.target.checked })}
            />
            Show Factors ({environmentalFactors.length})
          </label>
        </div>
        <button onClick={loadData} className="refresh-btn">
          Refresh
        </button>
      </div>

      {loading && <div className="map-loading">Loading map data...</div>}

      <MapContainer
        center={center}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />

        <WebSocketHandler onNewReport={handleNewReport} />

        {/* Render Crimes */}
        {filters.showCrimes && crimes.map((crime) => (
          crime.latitude && crime.longitude && (
            <Marker
              key={`crime-${crime.id}`}
              position={[crime.latitude, crime.longitude]}
              icon={crimeIcon}
            >
              <Popup>
                <div className="popup-content">
                  <h3>{crime.crime_type}</h3>
                  <p><strong>Date:</strong> {new Date(crime.occurred_at).toLocaleString()}</p>
                  <p><strong>Location:</strong> {crime.location_description}</p>
                  {crime.description && <p>{crime.description}</p>}
                  {crime.arrest_made && <p className="arrest-badge">Arrest Made</p>}
                </div>
              </Popup>
            </Marker>
          )
        ))}

        {/* Render User Reports */}
        {filters.showReports && reports.map((report) => (
          report.latitude && report.longitude && (
            <Marker
              key={`report-${report.id}`}
              position={[report.latitude, report.longitude]}
              icon={reportIcon}
            >
              <Popup>
                <div className="popup-content">
                  <h3>📝 User Report</h3>
                  <p><strong>Type:</strong> {report.crime_type}</p>
                  <p><strong>Status:</strong> {report.status}</p>
                  <p>{report.description}</p>
                  <p className="text-sm">Reported: {new Date(report.reported_at).toLocaleString()}</p>
                </div>
              </Popup>
            </Marker>
          )
        ))}

        {/* Render Environmental Factors */}
        {filters.showFactors && environmentalFactors.map((factor) => (
          factor.latitude && factor.longitude && (
            <React.Fragment key={`factor-${factor.id}`}>
              <Circle
                center={[factor.latitude, factor.longitude]}
                radius={200}
                pathOptions={{
                  color: factor.severity === 'high' ? '#e53e3e' : factor.severity === 'medium' ? '#dd6b20' : '#ecc94b',
                  fillOpacity: 0.2,
                }}
              />
              <Marker
                position={[factor.latitude, factor.longitude]}
              >
                <Popup>
                  <div className="popup-content">
                    <h3>
                      {factor.factor_type === 'poor_lighting' && <Lightbulb size={16} />}
                      {factor.factor_type === 'construction' && <Construction size={16} />}
                      {factor.factor_type === 'abandoned_building' && <AlertTriangle size={16} />}
                      {' '}{factor.factor_type.replace('_', ' ').toUpperCase()}
                    </h3>
                    <p><strong>Severity:</strong> {factor.severity}</p>
                    <p>{factor.description}</p>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          )
        ))}
      </MapContainer>

      <div className="map-legend">
        <h4>Legend</h4>
        <div className="legend-item">
          <span className="legend-marker crime"></span> Crime Incident
        </div>
        <div className="legend-item">
          <span className="legend-marker report"></span> User Report
        </div>
        <div className="legend-item">
          <span className="legend-circle high"></span> High Risk Factor
        </div>
      </div>
    </div>
  );
}

export default CrimeMap;
