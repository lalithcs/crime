import React, { useState, useEffect } from 'react';
import { alertsAPI, reportsAPI } from '../services/api';
import { AlertTriangle, X, Bell, MapPin } from 'lucide-react';
import './AlertsPanel.css';

function AlertsPanel() {
  const [alerts, setAlerts] = useState([]);
  const [recentReports, setRecentReports] = useState([]);
  const [visible, setVisible] = useState(true);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('alerts'); // 'alerts' or 'reports'

  useEffect(() => {
    loadData();
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [alertsRes, reportsRes] = await Promise.all([
        alertsAPI.getAlerts({ active_only: true }),
        reportsAPI.getReports({ limit: 10 }) // Get last 10 reports
      ]);
      setAlerts(alertsRes.data || []);
      setRecentReports(reportsRes.data || []);
    } catch (error) {
      console.error('Error loading data:', error);
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
        {(alerts.length + recentReports.length) > 0 && (
          <span className="alert-badge">{alerts.length + recentReports.length}</span>
        )}
      </button>
    );
  }

  return (
    <div className="alerts-panel">
      <div className="alerts-header">
        <div className="header-left">
          <AlertTriangle size={20} />
          <h4>Live Updates</h4>
          {(alerts.length + recentReports.length) > 0 && (
            <span className="count">{alerts.length + recentReports.length}</span>
          )}
        </div>
        <button className="minimize-btn" onClick={() => setVisible(false)}>
          <X size={18} />
        </button>
      </div>

      <div className="alerts-tabs">
        <button 
          className={`tab ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          Alerts ({alerts.length})
        </button>
        <button 
          className={`tab ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          Recent Reports ({recentReports.length})
        </button>
      </div>

      <div className="alerts-content">
        {loading && <div className="loading-alerts">Loading...</div>}
        
        {!loading && activeTab === 'alerts' && alerts.length === 0 && (
          <div className="no-alerts">
            <p>No active alerts at this time</p>
          </div>
        )}

        {!loading && activeTab === 'reports' && recentReports.length === 0 && (
          <div className="no-alerts">
            <p>No recent reports</p>
          </div>
        )}

        {!loading && activeTab === 'alerts' && alerts.length > 0 && (
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

        {!loading && activeTab === 'reports' && recentReports.length > 0 && (
          <div className="alerts-list">
            {recentReports.map((report) => (
              <div key={report.id} className="alert-item report-item">
                <div className="alert-header-item">
                  <MapPin size={16} className="report-icon" />
                  <span className="report-type">{report.crime_type}</span>
                  <span className={`status-badge ${report.status}`}>{report.status}</span>
                </div>
                <p className="report-desc">{report.description}</p>
                <p className="alert-location">
                  📍 {report.location_description || `${report.latitude.toFixed(4)}, ${report.longitude.toFixed(4)}`}
                </p>
                <p className="alert-time">
                  Reported: {new Date(report.reported_at).toLocaleString()}
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
