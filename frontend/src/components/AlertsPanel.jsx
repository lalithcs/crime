import React, { useState, useEffect } from 'react';
import { alertsAPI } from '../services/api';
import { AlertTriangle, X, Bell } from 'lucide-react';
import './AlertsPanel.css';

function AlertsPanel() {
  const [alerts, setAlerts] = useState([]);
  const [visible, setVisible] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
    // Refresh alerts every 30 seconds
    const interval = setInterval(loadAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadAlerts = async () => {
    try {
      const response = await alertsAPI.getAlerts({ active_only: true });
      setAlerts(response.data || []);
    } catch (error) {
      console.error('Error loading alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityClass = (severity) => {
    switch (severity) {
      case 'critical':
        return 'critical';
      case 'high':
        return 'high';
      case 'medium':
        return 'medium';
      default:
        return 'low';
    }
  };

  if (!visible) {
    return (
      <button className="alerts-toggle" onClick={() => setVisible(true)}>
        <Bell size={20} />
        {alerts.length > 0 && <span className="alert-badge">{alerts.length}</span>}
      </button>
    );
  }

  return (
    <div className="alerts-panel">
      <div className="alerts-header">
        <div className="header-left">
          <AlertTriangle size={20} />
          <h4>Active Alerts</h4>
          {alerts.length > 0 && <span className="count">{alerts.length}</span>}
        </div>
        <button className="minimize-btn" onClick={() => setVisible(false)}>
          <X size={18} />
        </button>
      </div>

      <div className="alerts-content">
        {loading && <div className="loading-alerts">Loading alerts...</div>}
        
        {!loading && alerts.length === 0 && (
          <div className="no-alerts">
            <p>No active alerts at this time</p>
          </div>
        )}

        {!loading && alerts.length > 0 && (
          <div className="alerts-list">
            {alerts.map((alert) => (
              <div key={alert.id} className={`alert-item ${getSeverityClass(alert.severity)}`}>
                <div className="alert-header-item">
                  <span className={`severity-badge ${alert.severity}`}>
                    {alert.severity}
                  </span>
                  <span className="alert-type">{alert.alert_type.replace('_', ' ')}</span>
                </div>
                <h5>{alert.title}</h5>
                <p>{alert.message}</p>
                {alert.latitude && alert.longitude && (
                  <p className="alert-location">
                    📍 {alert.latitude.toFixed(4)}, {alert.longitude.toFixed(4)} ({alert.radius_km}km radius)
                  </p>
                )}
                <p className="alert-time">
                  {new Date(alert.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AlertsPanel;
