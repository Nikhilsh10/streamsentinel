import React from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer'; // Optional, but usually needed with react-window. We will just use 100% width/height wrapper.

// Simple implementation without auto-sizer for simplicity if not installed
// We will assume parent passes width/height via a ref or we just use 100% and hope react-window handles it.
// Actually, let's use a simpler implementation since react-virtualized-auto-sizer wasn't requested.

export function EventFeed({ events, onEventClick }) {
    
  const Row = ({ index, style }) => {
    const ev = events[index];
    const ts = ev.timestamp.split("T")[1].replace("Z", ""); // roughly HH:MM:SS.mmm
    
    return (
      <div 
        style={style}
        className={`event-row ${ev.is_anomaly ? 'is-anomaly' : ''} severity-${ev.severity}`}
        onClick={() => onEventClick(ev)}
      >
        <div style={{ width: '60px' }}>
            <span className={`severity-badge ${ev.severity}`}>
                {ev.severity === 'NORMAL' ? 'NORM' : ev.severity}
            </span>
        </div>
        <div style={{ width: '120px', color: 'var(--text-muted)' }}>{ts}</div>
        <div style={{ width: '100px' }}>{ev.stream}</div>
        <div style={{ flex: 1 }}>
            Fusion: {ev.fusion_score.toFixed(3)}
        </div>
      </div>
    );
  };

  return (
    <div style={{ flex: 1, height: '100%' }}>
      {/* Fallback to simple scrollable div if react-window is tricky with flexbox */}
      <div style={{ height: '100%', overflowY: 'auto' }}>
        {events.map((ev, i) => (
           <Row key={ev.event_id} index={i} style={{}} />
        ))}
      </div>
    </div>
  );
}
