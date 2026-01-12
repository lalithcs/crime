import React, { useState, useRef, useEffect } from 'react';
import { chatbotAPI } from '../services/api';
import { X, Send, Bot } from 'lucide-react';
import './Chatbot.css';

function Chatbot({ onClose }) {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: '👋 Hello! I\'m your crime information assistant. Ask me anything or select a question below!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFAQ, setShowFAQ] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      type: 'user',
      text: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setShowFAQ(false);

    try {
      const response = await chatbotAPI.chat({ message: input });
      const botMessage = {
        type: 'bot',
        text: response.data.response,
        timestamp: new Date(),
        data: response.data.data,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'bot',
        text: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const faqs = [
    { q: 'How do I report a crime?', a: 'Click the "Report Crime" button at the top, select the crime type, describe what happened, choose your location from the dropdown, and submit. Your report will be reviewed and displayed on the map.' },
    { q: 'What is the Safety Route Planner?', a: 'The Safety Route Planner helps you find the safest path between two locations by avoiding high-crime areas. Select start and end locations from the dropdown, set your crime avoidance radius, and click "Calculate Safe Route". The route follows real roads and displays safety scores.' },
    { q: 'How do crime predictions work?', a: 'Our system uses ARIMA time-series analysis on historical crime data to predict future crime trends. It analyzes patterns like day of week, time, location, and crime types to forecast potential hotspots. Check the Dashboard for prediction charts.' },
    { q: 'What are crime hotspots?', a: 'Crime hotspots are areas with high concentrations of recent criminal activity. We identify them using clustering algorithms on crime data from the last 30 days. They are displayed on the Live Map with area names like "Madhapur" or "Gachibowli".' },
    { q: 'How accurate is the crime data?', a: 'The platform currently displays synthetic data for demonstration purposes (700 Hyderabad crimes + 300 Chicago crimes). In production, it would integrate with real police department APIs for live, verified data.' },
    { q: 'What does the safety score mean?', a: 'Safety scores range from 0-100, with higher being safer. For routes: 90+ = Very Safe, 70-90 = Safe, 50-70 = Moderate, below 50 = High Risk. The score considers avoided crime zones, route detours, and recent crime density.' },
    { q: 'Can I receive crime alerts?', a: 'Yes! The Alerts Panel on the right shows real-time community alerts and recent crime reports. Alerts update every 30 seconds via WebSocket. You can also enable email notifications for high-severity alerts in your area.' },
    { q: 'How is sentiment analysis used?', a: 'We analyze social media sentiment (Twitter) to predict crime trends. High negative sentiment in an area often correlates with increased crime risk. This runs locally using the Twitter sentiment analysis tool in the local_tools folder.' },
    { q: 'What crime types are tracked?', a: 'We track 10 major crime types: Theft, Assault, Burglary, Robbery, Battery, Vandalism, Motor Vehicle Theft, Narcotics, Weapons Violations, and Other. Each has unique icons and severity levels on the map.' },
    { q: 'Is my location data private?', a: 'Yes! Location data is only used for route calculations and crime reports. We don\'t store GPS coordinates long-term. When reporting crimes, you can select predefined area names instead of exact coordinates for privacy.' },
  ];

  const handleFAQClick = (faq) => {
    const userMessage = { type: 'user', text: faq.q, timestamp: new Date() };
    const botMessage = { type: 'bot', text: faq.a, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage, botMessage]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="chatbot-container" onClick={(e) => e.stopPropagation()}>
        <div className="chatbot-header">
          <div className="header-title">
            <Bot size={24} />
            <h3>Crime Information Assistant</h3>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="chatbot-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.type}`}>
              <div className="message-content">
                <div className="message-text">{msg.text}</div>
                <div className="message-time">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="message bot">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          {showFAQ && (
            <div className="faq-section-inline">
              <div className="faq-header">
                <h4>📚 Frequently Asked Questions</h4>
                <p>Click any question to see the answer</p>
              </div>
              <div className="faq-list">
                {faqs.map((faq, idx) => (
                  <button
                    key={idx}
                    className="faq-btn"
                    onClick={() => handleFAQClick(faq)}
                  >
                    <span className="faq-icon">Q:</span>
                    {faq.q}
                  </button>
                ))}
              </div>
              <button className="hide-faq-btn" onClick={() => setShowFAQ(false)}>
                Hide FAQs
              </button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="chatbot-input">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about crime information..."
            rows={1}
          />
          <button onClick={handleSend} disabled={loading || !input.trim()}>
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
