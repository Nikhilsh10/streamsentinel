import React from 'react';
import { useStreamSentinel } from './hooks/useStreamSentinel';
import EventFeed from './components/EventFeed';
import { FeatureBars } from './components/FeatureBars';
import { ReconstructionChart } from './components/ReconstructionChart';

export default function App() {
  const wsUrl = "ws://localhost:8000/ws";
  const { events, metrics, status } = useStreamSentinel(wsUrl);
  
  const [selectedEvent, setSelectedEvent] = React.useState(null);
  
  const recentAnomaly = events.find(e => e.is_anomaly) || null;
  const displayEvent = selectedEvent || recentAnomaly;

  const getStatusDisplay = () => {
    if (status === 'connected') return { text: 'LIVE', class: 'connected' };
    if (status === 'connecting') return { text: 'CONNECTING', class: 'connecting' };
    return { text: 'OFFLINE', class: 'disconnected' };
  };

  const stat = getStatusDisplay();

  // Averages calculation for stats
  const avgIf = events.length > 0 ? (events.reduce((a,b) => a + b.if_score, 0) / events.length).toFixed(3) : "0.000";
  const avgAe = events.length > 0 ? (events.reduce((a,b) => a + b.ae_score, 0) / events.length).toFixed(3) : "0.000";

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="header-bar">
        <div className="title">StreamSentinel</div>
        <div className="live-indicator">
          <div className={`live-dot ${stat.class}`}></div>
          {stat.text}
          <span style={{ color: 'var(--text-muted)', marginLeft: '1rem' }}>
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>

      {/* Stats Row */}
      <div className="stat-row">
        <div className="stat-panel">
          <div className="stat-label">Events/s</div>
          <div className="stat-value">{metrics.eps || 0}</div>
        </div>
        <div className="stat-panel">
          <div className="stat-label">Anomaly %</div>
          <div className="stat-value" style={{ color: metrics.anomalyRate > 10 ? 'var(--severity-high)' : 'inherit' }}>
            {metrics.anomalyRate || 0}%
          </div>
        </div>
        <div className="stat-panel">
          <div className="stat-label">IF Score</div>
          <div className="stat-value">avg {avgIf}</div>
        </div>
        <div className="stat-panel">
          <div className="stat-label">AE Score</div>
          <div className="stat-value">avg {avgAe}</div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content">
        <div className="panel" style={{ height: '300px' }}>
          <div className="panel-header">Reconstruction Error — Live (60s window)</div>
          <div className="panel-body">
            <ReconstructionChart events={events} />
          </div>
        </div>
        
        <div className="bottom-panels">
          <div className="panel">
            <div className="panel-header">Live Event Feed</div>
            <div className="panel-body">
              <EventFeed events={events} onEventClick={setSelectedEvent} />
            </div>
          </div>
          
          <div className="panel">
            <div className="panel-header">Last Anomaly — Feature Bars</div>
            <div className="panel-body">
              <FeatureBars event={displayEvent} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
