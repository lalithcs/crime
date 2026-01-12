import React, { useState } from 'react';
import { reportsAPI } from '../services/api';
import toast from 'react-hot-toast';
import { X, MapPin, Camera } from 'lucide-react';
import { ALL_LOCATIONS } from '../constants/locations';
import './ReportForm.css';

function ReportForm({ onClose }) {
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

  const handleLocationClick = () => {
    if (navigator.geolocation) {
      toast.loading('Getting your location...');
      navigator.geolocation.getCurrentPosition(
        (position) => {
          toast.dismiss();
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          
          // Find nearest predefined location
          let nearestLocation = ALL_LOCATIONS[0];
          let minDistance = Infinity;
          
          ALL_LOCATIONS.forEach(loc => {
            const distance = Math.sqrt(
              Math.pow(loc.lat - lat, 2) + Math.pow(loc.lng - lng, 2)
            );
            if (distance < minDistance) {
              minDistance = distance;
              nearestLocation = loc;
            }
          });
          
          setSelectedLocation(nearestLocation.name);
          setFormData({
            ...formData,
            latitude: nearestLocation.lat,
            longitude: nearestLocation.lng,
            location_description: nearestLocation.name,
          });
          toast.success(`Nearest location: ${nearestLocation.name}`);
        },
        (error) => {
          toast.dismiss();
          toast.error('Could not get location');
        }
      );
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
            <label>Location Description</label>
            <input
              type="text"
              name="location_description"
              value={formData.location_description}
              onChange={handleChange}
              placeholder="e.g., Street corner, Park, Store"
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

          <button
            type="button"
            className="location-btn"
            onClick={handleLocationClick}
          >
            <MapPin size={18} />
            Use My Current Location (Nearest Area)
          </button>

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
