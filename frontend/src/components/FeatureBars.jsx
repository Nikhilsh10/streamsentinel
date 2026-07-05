import React from 'react';

export function FeatureBars({ event }) {
  if (!event) {
    return <div className="feature-bar-container"><div style={{color: 'var(--text-muted)'}}>No anomalies yet.</div></div>;
  }

  // Calculate some mock "deviation score" for visual purposes
  // In reality, you'd calculate |val - mean| / std here based on known stats
  const getDeviation = (val, feature) => {
    // Just a placeholder normalization to [0,1] for display
    let num = parseFloat(val);
    if(isNaN(num)) return 0.5;
    
    // Randomize a bit based on string hash just to show bars
    let hash = 0;
    for (let i = 0; i < feature.length; i++) hash += feature.charCodeAt(i);
    return Math.abs(Math.sin(hash * num)) * 100; // 0-100%
  };

  const features = Object.entries(event.features)
    .filter(([k]) => !['event_id', 'stream', 'timestamp', 'is_injected_anomaly', 'device_id', 'user_id', 'country_code', 'merchant_category'].includes(k))
    .slice(0, 4);

  return (
    <div className="feature-bar-container">
      <div style={{ marginBottom: '1rem' }}>
        <div className="title">Event: {event.event_id.split("-")[0]}</div>
        <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Stream: {event.stream}</div>
      </div>
      
      {features.map(([key, val]) => {
        const pct = getDeviation(val, key);
        return (
          <div key={key} className="feature-bar-row">
            <div className="feature-name">{key}</div>
            <div className="feature-bar-bg">
              <div 
                className={`feature-bar-fill ${event.is_anomaly ? 'anomaly-'+event.severity : ''}`} 
                style={{ width: `${pct}%` }}
              ></div>
            </div>
            <div className="feature-val">{typeof val === 'number' ? val.toFixed(2) : val}</div>
          </div>
        );
      })}
      
      <div className="feature-bar-row" style={{marginTop: '1rem'}}>
        <div className="feature-name">Fusion Score</div>
        <div className="feature-bar-bg" style={{position: 'relative'}}>
            <div className={`feature-bar-fill ${event.is_anomaly ? 'anomaly-'+event.severity : ''}`} style={{ width: `${event.fusion_score * 100}%` }}></div>
            {/* Threshold marker */}
            <div style={{position: 'absolute', left: '65%', top: -2, bottom: -2, width: 2, backgroundColor: 'var(--severity-medium)', zIndex: 1}}></div>
        </div>
        <div className="feature-val">{event.fusion_score.toFixed(3)}</div>
      </div>
    </div>
  );
}
