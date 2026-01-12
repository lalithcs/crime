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
    { q: 'How can I find a safe route?', a: 'Go to the "Safe Routes" tab, select your start and end locations from the dropdown menu, and click "Calculate Safe Route". The system will show you the safest path that avoids high-crime areas.' },
    { q: 'What are crime predictions?', a: 'Crime predictions show areas where crimes are likely to occur based on historical patterns. You can view predicted hotspots on the Dashboard with charts showing trends over time.' },
    { q: 'What are crime hotspots?', a: 'Crime hotspots are areas with high concentrations of recent criminal activity. They appear on the Live Map with area names like "Madhapur" or "Gachibowli" and are color-coded by severity.' },
    { q: 'How recent is the crime data?', a: 'The platform displays crime data from the last 30-90 days. Data is updated regularly to ensure you have the most current information about your area.' },
    { q: 'What do the safety scores mean?', a: 'Safety scores range from 0-100, with higher being safer. 90+ is Very Safe, 70-90 is Safe, 50-70 is Moderate Risk, and below 50 is High Risk. Scores are based on recent crime activity in the area.' },
    { q: 'Can I get crime alerts?', a: 'Yes! The Alerts Panel on the right shows real-time community alerts and recent crime reports. Alerts update automatically every 30 seconds so you stay informed.' },
    { q: 'What types of crimes are tracked?', a: 'We track Theft, Assault, Burglary, Robbery, Battery, Vandalism, Motor Vehicle Theft, Narcotics, Weapons Violations, and other criminal activities. Each type has a unique icon on the map.' },
    { q: 'Is my information safe?', a: 'Yes! Your location data is only used for calculations and reports. We don\'t store personal GPS coordinates. You can select general area names instead of exact addresses for added privacy.' },
    { q: 'How do I use the map?', a: 'The Live Map shows crime incidents as red markers, user reports as blue markers, and environmental risk factors as yellow circles. Click any marker to see details. Use the filters at the top to customize what you see.' },
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

          {!showFAQ && (
            <div className="show-faq-container">
              <button className="show-faq-btn" onClick={() => setShowFAQ(true)}>
                📚 Show FAQs
              </button>
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
