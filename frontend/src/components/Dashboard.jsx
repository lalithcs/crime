import React, { useState, useEffect } from 'react';
import { crimesAPI, predictionsAPI } from '../services/api';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, AlertCircle, CheckCircle, Activity } from 'lucide-react';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, predRes, hotspotsRes] = await Promise.all([
        crimesAPI.getStats(30),
        predictionsAPI.predict({ days_ahead: 7 }),
        predictionsAPI.getHotspots(7),
      ]);

      setStats(statsRes.data);
      setPredictions(predRes.data.predictions || []);
      setHotspots(hotspotsRes.data.hotspots || []);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Crime Analytics Dashboard</h2>
        <button onClick={loadDashboardData} className="refresh-btn">Refresh</button>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon crime">
            <Activity size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Total Crimes (30 days)</p>
            <h3 className="stat-value">{stats?.total_crimes || 0}</h3>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon arrest">
            <CheckCircle size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Arrests Made</p>
            <h3 className="stat-value">{stats?.arrests || 0}</h3>
            <p className="stat-sub">{stats?.arrest_rate || 0}% arrest rate</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon hotspot">
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Crime Hotspots</p>
            <h3 className="stat-value">{hotspots.length}</h3>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon prediction">
            <AlertCircle size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Next 7 Days Forecast</p>
            <h3 className="stat-value">
              {predictions.reduce((sum, p) => sum + p.predicted_crimes, 0)}
            </h3>
            <p className="stat-sub">predicted crimes</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        {/* Crime Distribution */}
        <div className="chart-card">
          <h3>Crime Distribution by Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats?.by_type || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Predictions */}
        <div className="chart-card">
          <h3>7-Day Crime Forecast (ARIMA Model)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={predictions}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="predicted_crimes" stroke="#667eea" strokeWidth={2} name="Predicted" />
              <Line type="monotone" dataKey="upper_bound" stroke="#e53e3e" strokeDasharray="3 3" name="Upper Bound" />
              <Line type="monotone" dataKey="lower_bound" stroke="#48bb78" strokeDasharray="3 3" name="Lower Bound" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Hotspots Table */}
      <div className="hotspots-section">
        <h3>Predicted Crime Hotspots</h3>
        <div className="hotspots-table">
          <table>
            <thead>
              <tr>
                <th>Location</th>
                <th>Current Crimes</th>
                <th>Predicted Increase</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {hotspots.slice(0, 10).map((hotspot, idx) => (
                <tr key={idx}>
                  <td>{hotspot.latitude.toFixed(4)}, {hotspot.longitude.toFixed(4)}</td>
                  <td>{hotspot.crime_count}</td>
                  <td>+{hotspot.predicted_increase}</td>
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
    </div>
  );
}

export default Dashboard;
