import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const crimesAPI = {
  getCrimes: (params) => api.get('/crimes/', { params }),
  getStats: (days = 30) => api.get('/crimes/stats', { params: { days } }),
  getHeatmap: (params) => api.get('/crimes/heatmap', { params }),
};

export const reportsAPI = {
  createReport: (data) => api.post('/reports/', data),
  getReports: (params) => api.get('/reports/', { params }),
};

export const predictionsAPI = {
  predict: (data) => api.post('/predictions/', data),
  getHotspots: (days = 7) => api.get('/predictions/hotspots', { params: { days_ahead: days } }),
};

export const routesAPI = {
  getSafeRoute: (data) => api.post('/routes/safe', data),
  compareRoutes: (data) => api.post('/routes/compare', data),
};

export const sentimentAPI = {
  analyze: (data) => api.post('/sentiment/', data),
  getTrends: (params) => api.get('/sentiment/trends', { params }),
};

export const chatbotAPI = {
  chat: (data) => api.post('/chatbot/', data),
};

export const alertsAPI = {
  getAlerts: (params) => api.get('/alerts/', { params }),
  createAlert: (data) => api.post('/alerts/', data),
};

export const causesAPI = {
  getFactors: (params) => api.get('/causes/', { params }),
  reportFactor: (data) => api.post('/causes/', data),
};

export default api;
