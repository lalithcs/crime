import React, { useState, useEffect } from 'react';
import { sentimentAPI } from '../services/api';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, Smile, Meh, Frown } from 'lucide-react';
import toast from 'react-hot-toast';
import './SentimentPanel.css';

function SentimentPanel() {
  const [trends, setTrends] = useState(null);
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrends();
  }, []);

  const loadTrends = async () => {
    setLoading(true);
    try {
      const response = await sentimentAPI.getTrends({ days: 30 });
      setTrends(response.data);
    } catch (error) {
      console.error('Error loading trends:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setAnalyzing(true);
    try {
      const response = await sentimentAPI.analyze({ text });
      setResult(response.data);
      toast.success('Sentiment analyzed!');
      // Reload trends
      loadTrends();
    } catch (error) {
      console.error('Error analyzing sentiment:', error);
      toast.error('Failed to analyze sentiment');
    } finally {
      setAnalyzing(false);
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <Smile size={24} className="sentiment-icon positive" />;
      case 'negative':
        return <Frown size={24} className="sentiment-icon negative" />;
      default:
        return <Meh size={24} className="sentiment-icon neutral" />;
    }
  };

  return (
    <div className="sentiment-panel">
      <div className="sentiment-header">
        <h2><TrendingUp size={24} /> Citizen Sentiment Analysis</h2>
      </div>

      <div className="sentiment-content">
        {/* Analyze Form */}
        <div className="analyze-section card">
          <h3>Analyze New Text</h3>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to analyze sentiment (e.g., community feedback, social media post, survey response)..."
            rows={4}
          />
          <button onClick={handleAnalyze} disabled={analyzing} className="analyze-btn">
            {analyzing ? 'Analyzing...' : 'Analyze Sentiment'}
          </button>

          {result && (
            <div className="sentiment-result">
              <div className="result-header">
                {getSentimentIcon(result.sentiment)}
                <h4>{result.sentiment.toUpperCase()}</h4>
              </div>
              <div className="result-details">
                <div className="detail-row">
                  <span>Sentiment Score:</span>
                  <strong>{result.sentiment_score.toFixed(3)}</strong>
                </div>
                <div className="detail-row">
                  <span>Confidence:</span>
                  <strong>{(result.confidence * 100).toFixed(1)}%</strong>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Trends */}
        {!loading && trends && (
          <>
            <div className="trends-overview card">
              <h3>Sentiment Overview (Last 30 Days)</h3>
              <div className="sentiment-stats">
                <div className="stat-item">
                  <Smile className="positive" />
                  <div>
                    <p className="stat-value">{trends.sentiment_distribution.positive}</p>
                    <p className="stat-label">Positive</p>
                  </div>
                </div>
                <div className="stat-item">
                  <Meh className="neutral" />
                  <div>
                    <p className="stat-value">{trends.sentiment_distribution.neutral}</p>
                    <p className="stat-label">Neutral</p>
                  </div>
                </div>
                <div className="stat-item">
                  <Frown className="negative" />
                  <div>
                    <p className="stat-value">{trends.sentiment_distribution.negative}</p>
                    <p className="stat-label">Negative</p>
                  </div>
                </div>
              </div>
              <div className="overall-sentiment">
                <h4>Overall Sentiment:</h4>
                <span className={`sentiment-badge ${trends.overall_sentiment}`}>
                  {trends.overall_sentiment.toUpperCase()}
                </span>
                <p>Average Score: {trends.average_sentiment_score.toFixed(3)}</p>
              </div>
            </div>

            {/* Distribution Chart */}
            <div className="chart-card card">
              <h3>Sentiment Distribution</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart
                  data={[
                    { name: 'Positive', count: trends.sentiment_distribution.positive },
                    { name: 'Neutral', count: trends.sentiment_distribution.neutral },
                    { name: 'Negative', count: trends.sentiment_distribution.negative },
                  ]}
                >
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#667eea" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Weekly Trends */}
            {trends.weekly_trends && trends.weekly_trends.length > 0 && (
              <div className="chart-card card">
                <h3>Weekly Sentiment Trends</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={trends.weekly_trends}>
                    <XAxis dataKey="week" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="avg_sentiment" stroke="#667eea" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </>
        )}

        {loading && <div className="loading">Loading sentiment data...</div>}
      </div>
    </div>
  );
}

export default SentimentPanel;
