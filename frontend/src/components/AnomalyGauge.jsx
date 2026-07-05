export default function AnomalyGauge({ value = 0 }) {
  // value: anomaly_rate_pct (0–100 float, but realistically 0–20)
  const MAX = 15;
  const pct = Math.min(value, MAX) / MAX;
  const angle = -135 + pct * 270;   // sweep from -135° to +135°

  // Color: green < 4%, yellow 4-8%, red > 8%
  const color = value < 4
    ? "#10B981"
    : value < 8
    ? "#F59E0B"
    : "#EF4444";

  // SVG arc math
  const cx = 60, cy = 60, r = 44;
  const toRad = (deg) => (deg * Math.PI) / 180;
  const arcX = (deg) => cx + r * Math.cos(toRad(deg));
  const arcY = (deg) => cy + r * Math.sin(toRad(deg));

  const startDeg = -135;
  const endDeg = -135 + pct * 270;
  const largeArc = pct * 270 > 180 ? 1 : 0;

  const trackPath = `M ${arcX(startDeg)} ${arcY(startDeg)}
    A ${r} ${r} 0 1 1 ${arcX(134)} ${arcY(134)}`;
  const fillPath = pct > 0
    ? `M ${arcX(startDeg)} ${arcY(startDeg)}
       A ${r} ${r} 0 ${largeArc} 1 ${arcX(endDeg)} ${arcY(endDeg)}`
    : "";

  return (
    <div className="gauge-container">
      <svg viewBox="0 0 120 80" width="140" height="94">
        <path
          d={trackPath}
          fill="none"
          stroke="var(--bg-elevated)"
          strokeWidth="8"
          strokeLinecap="round"
        />
        {fillPath && (
          <path
            d={fillPath}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
          />
        )}
        <text
          x={cx} y={cy + 4}
          textAnchor="middle"
          fontSize="14"
          fontWeight="600"
          fontFamily="JetBrains Mono, monospace"
          fill={color}
        >
          {Number(value).toFixed(1)}%
        </text>
        <text
          x={cx} y={cy + 18}
          textAnchor="middle"
          fontSize="7"
          fill="var(--text-muted)"
          fontFamily="JetBrains Mono, monospace"
        >
          ANOMALY RATE
        </text>
      </svg>
    </div>
  );
}
