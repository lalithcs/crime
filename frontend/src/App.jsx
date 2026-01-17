import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import CrimeMap from './components/CrimeMap';
import Dashboard from './components/Dashboard';
import ReportForm from './components/ReportForm';
import Chatbot from './components/Chatbot';
import RoutePlanner from './components/RoutePlanner';
import AlertsPanel from './components/AlertsPanel';
import { Activity, Map, MessageSquare, Route } from 'lucide-react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('map');
  const [showReportForm, setShowReportForm] = useState(false);
  const [showChatbot, setShowChatbot] = useState(false);

  return (
    <div className="app">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <Activity size={28} />
            <h1>CrimeScope</h1>
          </div>
          <div className="header-actions">
            <button 
              className="btn-primary"
              onClick={() => setShowReportForm(true)}
            >
              Report Crime
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === 'map' ? 'active' : ''}`}
          onClick={() => setActiveTab('map')}
        >
          <Map size={18} />
          Live Map
        </button>
        <button
          className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <Activity size={18} />
          Dashboard
        </button>
        <button
          className={`nav-tab ${activeTab === 'route' ? 'active' : ''}`}
          onClick={() => setActiveTab('route')}
        >
          <Route size={18} />
          Safe Routes
        </button>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'map' && <CrimeMap />}
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'route' && <RoutePlanner />}
      </main>

      {/* Floating Chatbot Button */}
      <button
        className="chatbot-fab"
        onClick={() => setShowChatbot(!showChatbot)}
      >
        <MessageSquare size={24} />
      </button>

      {/* Alerts Panel (Always visible) */}
      <AlertsPanel />

      {/* Modals */}
      {showReportForm && (
        <ReportForm onClose={() => setShowReportForm(false)} />
      )}
      {showChatbot && (
        <Chatbot onClose={() => setShowChatbot(false)} />
      )}
    </div>
  );
}

export default App;
