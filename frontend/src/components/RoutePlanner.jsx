import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import { routesAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Navigation, MapPin, Clock, Shield, AlertTriangle } from 'lucide-react';
import './RoutePlanner.css';

function RoutePlanner() {
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    start_lat: 17.385,  // Hyderabad - Hitech City
    start_lng: 78.486,
    end_lat: 17.445,    // Hyderabad - Madhapur
    end_lng: 78.380,
    avoid_crime_radius_km: 0.5,
  });
  const [showComparison, setShowComparison] = useState(false);
  const [comparison, setComparison] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: parseFloat(e.target.value),
    });
  };

  const handleCalculateRoute = async () => {
    setLoading(true);
    try {
      const response = await routesAPI.getSafeRoute(formData);
      setRouteData(response.data);
      toast.success('Safe route calculated!');
    } catch (error) {
      console.error('Error calculating route:', error);
      toast.error('Failed to calculate route');
    } finally {
      setLoading(false);
    }
  };

  const handleCompareRoutes = async () => {
    setLoading(true);
    try {
      const response = await routesAPI.compareRoutes(formData);
      setComparison(response.data);
      setShowComparison(true);
      toast.success('Routes compared!');
    } catch (error) {
      console.error('Error comparing routes:', error);
      toast.error('Failed to compare routes');
    } finally {
      setLoading(false);
    }
  };

  const handleUseCurrentLocation = (field) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          if (field === 'start') {
            setFormData({
              ...formData,
              start_lat: position.coords.latitude,
              start_lng: position.coords.longitude,
            });
          } else {
            setFormData({
              ...formData,
              end_lat: position.coords.latitude,
              end_lng: position.coords.longitude,
            });
          }
          toast.success('Location updated!');
        },
        (error) => {
          toast.error('Could not get location');
        }
      );
    }
  };

  return (
    <div className="route-planner">
      <div className="route-sidebar">
        <h2><Navigation size={24} /> Safety Route Planner</h2>

        <div className="route-form">
          <div className="location-section">
            <h3>Start Location</h3>
            <div className="coord-inputs">
              <input
                type="number"
                name="start_lat"
                value={formData.start_lat}
                onChange={handleChange}
                placeholder="Latitude"
                step="0.000001"
              />
              <input
                type="number"
                name="start_lng"
                value={formData.start_lng}
                onChange={handleChange}
                placeholder="Longitude"
                step="0.000001"
              />
            </div>
            <button
              className="loc-btn"
              onClick={() => handleUseCurrentLocation('start')}
            >
              <MapPin size={16} /> Use Current Location
            </button>
          </div>

          <div className="location-section">
            <h3>Destination</h3>
            <div className="coord-inputs">
              <input
                type="number"
                name="end_lat"
                value={formData.end_lat}
                onChange={handleChange}
                placeholder="Latitude"
                step="0.000001"
              />
              <input
                type="number"
                name="end_lng"
                value={formData.end_lng}
                onChange={handleChange}
                placeholder="Longitude"
                step="0.000001"
              />
            </div>
            <button
              className="loc-btn"
              onClick={() => handleUseCurrentLocation('end')}
            >
              <MapPin size={16} /> Use Current Location
            </button>
          </div>

          <div className="form-group">
            <label>Crime Avoidance Radius (km)</label>
            <input
              type="number"
              name="avoid_crime_radius_km"
              value={formData.avoid_crime_radius_km}
              onChange={handleChange}
              min="0.1"
              max="5"
              step="0.1"
            />
          </div>

          <div className="action-buttons">
            <button
              className="btn-calculate"
              onClick={handleCalculateRoute}
              disabled={loading}
            >
              {loading ? 'Calculating...' : 'Calculate Safe Route'}
            </button>
            <button
              className="btn-compare"
              onClick={handleCompareRoutes}
              disabled={loading}
            >
              Compare Routes
            </button>
          </div>
        </div>

        {routeData && (
          <div className="route-info">
            <h3>Route Details</h3>
            <div className="info-row">
              <Clock size={18} />
              <div>
                <span className="label">Duration:</span>
                <span className="value">{routeData.duration_minutes} min</span>
              </div>
            </div>
            <div className="info-row">
              <Navigation size={18} />
              <div>
                <span className="label">Distance:</span>
                <span className="value">{routeData.distance_km} km</span>
              </div>
            </div>
            <div className="info-row">
              <Shield size={18} />
              <div>
                <span className="label">Safety Score:</span>
                <span className={`value score-${Math.floor(routeData.safety_score / 20)}`}>
                  {routeData.safety_score}/100
                </span>
              </div>
            </div>
            <div className="info-row">
              <AlertTriangle size={18} />
              <div>
                <span className="label">Avoided Zones:</span>
                <span className="value">{routeData.avoided_crime_zones}</span>
              </div>
            </div>
          </div>
        )}

        {showComparison && comparison && (
          <div className="comparison-panel">
            <h3>Route Comparison</h3>
            <div className="comparison-grid">
              <div className="comparison-col">
                <h4>Safe Route</h4>
                <p>Distance: {comparison.safe_route.distance_km} km</p>
                <p>Time: {comparison.safe_route.duration_minutes} min</p>
                <p>Safety: {comparison.safe_route.safety_score}/100</p>
                <p>Avoided: {comparison.safe_route.avoided_zones} zones</p>
              </div>
              <div className="comparison-col">
                <h4>Direct Route</h4>
                <p>Distance: {comparison.direct_route.distance_km} km</p>
                <p>Time: {comparison.direct_route.duration_minutes} min</p>
                <p>Safety: {comparison.direct_route.safety_score}/100</p>
                <p>Avoided: {comparison.direct_route.avoided_zones} zones</p>
              </div>
            </div>
            <div className="recommendation">
              <strong>Recommendation:</strong> {comparison.comparison.recommendation === 'safe_route' ? '✅ Use Safe Route' : '⚡ Direct Route OK'}
            </div>
          </div>
        )}
      </div>

      <div className="route-map">
        {routeData ? (
          <MapContainer
            center={[formData.start_lat, formData.start_lng]}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            
            {/* Start Marker */}
            <Marker position={[formData.start_lat, formData.start_lng]}>
              <Popup>Start Location</Popup>
            </Marker>

            {/* End Marker */}
            <Marker position={[formData.end_lat, formData.end_lng]}>
              <Popup>Destination</Popup>
            </Marker>

            {/* Route Line */}
            <Polyline
              positions={routeData.route}
              color="#667eea"
              weight={4}
              opacity={0.8}
            />

            {/* Waypoints */}
            {routeData.waypoints.map((wp, idx) => (
              wp.type === 'waypoint' && (
                <Marker key={idx} position={[wp.lat, wp.lng]}>
                  <Popup>Safety Waypoint</Popup>
                </Marker>
              )
            ))}
          </MapContainer>
        ) : (
          <div className="map-placeholder">
            <Navigation size={48} />
            <p>Calculate a route to see it on the map</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default RoutePlanner;
