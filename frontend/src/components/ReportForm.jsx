import React, { useState } from 'react';
import { reportsAPI } from '../services/api';
import toast from 'react-hot-toast';
import { X, MapPin } from 'lucide-react';
import { ALL_LOCATIONS } from '../constants/locations';
import './ReportForm.css';

function ReportForm({ onClose, onLocationUpdate }) {
  const [selectedLocation, setSelectedLocation] = useState(ALL_LOCATIONS[0].name);
  const [formData, setFormData] = useState({
    user_id: 'user_' + Math.random().toString(36).substr(2, 9),
    crime_type: '',
    description: '',
    latitude: ALL_LOCATIONS[0].lat,
    longitude: ALL_LOCATIONS[0].lng,
    location_description: ALL_LOCATIONS[0].name,
  });
  const [submitting, setSubmitting] = useState(false);

  const crimeTypes = [
    'THEFT',
    'BATTERY',
    'ASSAULT',
    'BURGLARY',
    'ROBBERY',
    'VANDALISM',
    'MOTOR VEHICLE THEFT',
    'NARCOTICS',
    'WEAPONS VIOLATION',
    'OTHER',
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleLocationChange = (locationName) => {
    const location = ALL_LOCATIONS.find(loc => loc.name === locationName);
    if (location) {
      setSelectedLocation(locationName);
      setFormData({
        ...formData,
        latitude: location.lat,
        longitude: location.lng,
        location_description: location.name,
      });
    }
  };

  const handleLocationClick = async () => {
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
            
            // Add road/street
            if (address.road) {
              locationParts.push(address.road);
            } else if (address.neighbourhood) {
              locationParts.push(address.neighbourhood);
            }
            
            // Add area/suburb
            if (address.suburb || address.city_district) {
              locationParts.push(address.suburb || address.city_district);
            }
            
            // Add city
            if (address.city || address.town || address.village) {
              locationParts.push(address.city || address.town || address.village);
            }
            
            const locationName = locationParts.join(', ') || data.display_name?.split(',').slice(0, 3).join(',') || 'Unknown Location';
            
            setSelectedLocation(`📍 ${locationName.substring(0, 50)}`);
            setFormData({
              ...formData,
              latitude: lat,
              longitude: lng,
              location_description: locationName,
            });
            
            // Update parent component with user's location for map marker
            if (onLocationUpdate) {
              onLocationUpdate({
                lat,
                lng,
                name: locationName,
                accuracy
              });
            }
            
            toast.dismiss();
            toast.success(`Location: ${locationName.substring(0, 40)}... (±${accuracy.toFixed(0)}m)`, { duration: 4000 });
          } catch (error) {
            console.error('Geocoding error:', error);
            // Fallback to coordinates if geocoding fails
            const fallbackName = `GPS Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`;
            setSelectedLocation(fallbackName);
            setFormData({
              ...formData,
              latitude: lat,
              longitude: lng,
              location_description: `GPS: ${lat.toFixed(6)}, ${lng.toFixed(6)}`,
            });
            toast.dismiss();
            toast.success(`Location found! Accuracy: ${accuracy.toFixed(0)}m`);
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.crime_type || !formData.description) {
      toast.error('Please fill in all required fields');
      return;
    }

    setSubmitting(true);
    try {
      await reportsAPI.createReport(formData);
      toast.success('Crime report submitted successfully!');
      onClose();
    } catch (error) {
      console.error('Error submitting report:', error);
      toast.error('Failed to submit report');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Report a Crime</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="report-form">
          <div className="form-group">
            <label>Crime Type *</label>
            <select
              name="crime_type"
              value={formData.crime_type}
              onChange={handleChange}
              required
            >
              <option value="">Select a crime type</option>
              {crimeTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe what happened..."
              rows={4}
              required
            />
          </div>

          <div className="form-group">
            <label>Location *</label>
            <select
              className="location-select"
              value={selectedLocation}
              onChange={(e) => handleLocationChange(e.target.value)}
              required
            >
              {ALL_LOCATIONS.map((loc) => (
                <option key={loc.name} value={loc.name}>
                  {loc.name} {loc.city ? `(${loc.city})` : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Location Description (Auto-filled from GPS)</label>
            <input
              type="text"
              name="location_description"
              value={formData.location_description}
              onChange={handleChange}
              placeholder="e.g., Starbucks Coffee, Road No 36, Jubilee Hills"
            />
          </div>

          <button
            type="button"
            className="location-btn"
            onClick={handleLocationClick}
          >
            <MapPin size={18} />
            Use My Exact GPS Location
          </button>

          <div className="coordinates-display">
            <small>
              Coordinates: {formData.latitude.toFixed(6)}, {formData.longitude.toFixed(6)}
            </small>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Report'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ReportForm;
