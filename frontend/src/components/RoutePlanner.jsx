import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import { routesAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Navigation, MapPin, Clock, Shield, AlertTriangle } from 'lucide-react';
import { ALL_LOCATIONS } from '../constants/locations';
import './RoutePlanner.css';

function RoutePlanner() {
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedStartLocation, setSelectedStartLocation] = useState(ALL_LOCATIONS[2].name); // Hitech City
  const [selectedEndLocation, setSelectedEndLocation] = useState(ALL_LOCATIONS[0].name); // Madhapur
  const [formData, setFormData] = useState({
    start_lat: ALL_LOCATIONS[2].lat,
    start_lng: ALL_LOCATIONS[2].lng,
    end_lat: ALL_LOCATIONS[0].lat,
    end_lng: ALL_LOCATIONS[0].lng,
    avoid_crime_radius_km: 0.5,
  });
  const [showComparison, setShowComparison] = useState(false);
  const [comparison, setComparison] = useState(null);

  const handleLocationChange = (type, locationName) => {
    const location = ALL_LOCATIONS.find(loc => loc.name === locationName);
    if (location) {
      if (type === 'start') {
        setSelectedStartLocation(locationName);
        setFormData({
          ...formData,
          start_lat: location.lat,
          start_lng: location.lng,
        });
      } else {
        setSelectedEndLocation(locationName);
        setFormData({
          ...formData,
          end_lat: location.lat,
          end_lng: location.lng,
        });
      }
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: parseFloat(e.target.value),
    });
  };

  const handleGetCurrentLocation = (type) => {
    if (navigator.geolocation) {
      toast.loading('Getting your location...');
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          const accuracy = position.coords.accuracy;
          
          toast.loading('Getting location name...');
          
          try {
            // Reverse geocode to get location name with building details
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=19&addressdetails=1&extratags=1&namedetails=1`,
              {
                headers: {
                  'User-Agent': 'CrimeScope/1.0'
                }
              }
            );
            const data = await response.json();
            
            // Extract meaningful location info with building/POI priority
            const address = data.address || {};
            
            // Priority: Building name > Shop/Amenity > Road > Area
            const buildingName = data.namedetails?.name || 
                               data.extratags?.building || 
                               address.building || 
                               address.shop || 
                               address.amenity || 
                               address.tourism || 
                               address.office || 
                               address.commercial;
            
            const locationParts = [];
            
            // Add building/POI name if available
            if (buildingName && buildingName !== address.road) {
              locationParts.push(buildingName);
            }
            
            // Add road/street or neighbourhood
            if (address.road) {
              locationParts.push(address.road);
            } else if (address.neighbourhood) {
              locationParts.push(address.neighbourhood);
            }
            
            // Add area
            if (address.suburb || address.city_district) {
              locationParts.push(address.suburb || address.city_district);
            }
            
            const locationName = locationParts.slice(0, 2).join(', ') || data.display_name?.split(',').slice(0, 2).join(',') || `GPS (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
            
            if (type === 'start') {
              setSelectedStartLocation(`📍 ${locationName.substring(0, 40)}`);
              setFormData({
                ...formData,
                start_lat: lat,
                start_lng: lng,
              });
            } else {
              setSelectedEndLocation(`📍 ${locationName.substring(0, 40)}`);
              setFormData({
                ...formData,
                end_lat: lat,
                end_lng: lng,
              });
            }
            
            toast.dismiss();
            toast.success(`${type === 'start' ? 'Start' : 'Destination'}: ${locationName.substring(0, 35)}...`, { duration: 3000 });
          } catch (error) {
            console.error('Geocoding error:', error);
            // Fallback to coordinates if geocoding fails
            const locationName = `My Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
            
            if (type === 'start') {
              setSelectedStartLocation(locationName);
              setFormData({
                ...formData,
                start_lat: lat,
                start_lng: lng,
              });
            } else {
              setSelectedEndLocation(locationName);
              setFormData({
                ...formData,
                end_lat: lat,
                end_lng: lng,
              });
            }
            
            toast.dismiss();
            toast.success(`${type === 'start' ? 'Start' : 'End'} location set! Accuracy: ${accuracy.toFixed(0)}m`);
          }
        },
        (error) => {
          toast.dismiss();
          if (error.code === error.PERMISSION_DENIED) {
            toast.error('Location permission denied');
          } else if (error.code === error.POSITION_UNAVAILABLE) {
            toast.error('Location unavailable');
          } else if (error.code === error.TIMEOUT) {
            toast.error('Location request timed out');
          } else {
            toast.error('Could not get location');
          }
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    } else {
      toast.error('Geolocation not supported by browser');
    }
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
    handleGetCurrentLocation(field);
  };

  return (
    <div className="route-planner">
      <div className="route-sidebar">
        <h2><Navigation size={24} /> Safety Route Planner</h2>

        <div className="route-form">
          <div className="location-section">
            <h3>Start Location</h3>
            <select
              className="location-select"
              value={selectedStartLocation}
              onChange={(e) => handleLocationChange('start', e.target.value)}
            >
              {ALL_LOCATIONS.map((loc) => (
                <option key={`start-${loc.name}`} value={loc.name}>
                  {loc.name} {loc.city ? `(${loc.city})` : ''}
                </option>
              ))}
            </select>
            <button
              className="loc-btn"
              onClick={() => handleUseCurrentLocation('start')}
            >
              <MapPin size={16} /> Use Current Location
            </button>
          </div>

          <div className="location-section">
            <h3>Destination</h3>
            <select
              className="location-select"
              value={selectedEndLocation}
              onChange={(e) => handleLocationChange('end', e.target.value)}
            >
              {ALL_LOCATIONS.map((loc) => (
                <option key={`end-${loc.name}`} value={loc.name}>
                  {loc.name} {loc.city ? `(${loc.city})` : ''}
                </option>
              ))}
            </select>
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
