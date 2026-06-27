import { useState } from "react";

const SEVERITY_CLASS = {
  HIGH:   "anomaly-HIGH",
  MEDIUM: "anomaly-MEDIUM",
  LOW:    "anomaly-LOW",
  NORMAL: "",
};

const BADGE_CLASS = {
  HIGH:   "badge-HIGH",
  MEDIUM: "badge-MEDIUM",
  LOW:    "badge-LOW",
  NORMAL: "badge-NORMAL",
};

function formatTime(isoString) {
  try {
    return new Date(isoString).toLocaleTimeString("en-GB", {
      hour: "2-digit", minute: "2-digit", second: "2-digit",
      fractionalSecondDigits: 3,
    });
  } catch {
    return isoString;
  }
}

function formatFeatures(features, stream) {
  if (stream === "sensor") {
    return `temp:${Number(features.temperature ?? 0).toFixed(1)}°  `
         + `vib:${Number(features.vibration ?? 0).toFixed(3)}  `
         + `pres:${Number(features.pressure ?? 0).toFixed(1)}`;
  }
  return `$${Number(features.amount ?? 0).toFixed(2)}  `
       + `vel:${features.velocity_30s ?? 0}  `
       + `hr:${features.hour_of_day ?? 0}`;
}

export default function EventFeed({ events, streamFilter }) {
  const [expanded, setExpanded] = useState(null);

  const filtered = streamFilter === "all"
    ? events
    : events.filter((e) => e.stream === streamFilter);

  if (filtered.length === 0) {
    return (
      <div className="empty-state">
        <span>Waiting for events...</span>
        <span style={{ fontSize: "10px" }}>Check that Kafka producer is running</span>
      </div>
    );
  }

  return (
    <div className="event-feed">
      {filtered.map((event) => {
        const isExpanded = expanded === event.event_id;
        const rowClass = [
          "event-row",
          event.severity !== "NORMAL" ? `anomaly-${event.severity}` : "",
        ].filter(Boolean).join(" ");

        return (
          <div
            key={event.event_id}
            className={rowClass}
            onClick={() => setExpanded(isExpanded ? null : event.event_id)}
          >
            <span className={`severity-badge ${BADGE_CLASS[event.severity]}`}>
              {event.severity}
            </span>

            <div className="event-meta">
              <div className="event-time">
                {formatTime(event.timestamp)}
                {" "}
                <span className={`stream-pill stream-${event.stream}`}>
                  {event.stream}
                </span>
              </div>
              <div className="event-details">
                {formatFeatures(event.features, event.stream)}
              </div>
              <div className="event-scores">
                fusion:{Number(event.fusion_score).toFixed(3)}
                {" | "}
                if:{Number(event.if_score).toFixed(3)}
                {" | "}
                ae:{Number(event.ae_score).toFixed(3)}
                {" | "}
                {Number(event.inference_latency_ms).toFixed(1)}ms
              </div>

              {isExpanded && (
                <div style={{
                  marginTop: "6px", padding: "8px",
                  background: "var(--bg-elevated)",
                  borderRadius: "4px", fontSize: "10px",
                  color: "var(--text-muted)", lineHeight: "1.8"
                }}>
                  {Object.entries(event.features).map(([k, v]) => (
                    <div key={k}>
                      <span style={{ color: "var(--text-primary)" }}>{k}:</span> {v}
                    </div>
                  ))}
                  <div style={{ marginTop: "4px", color: "var(--text-dim)" }}>
                    id: {event.event_id}
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
