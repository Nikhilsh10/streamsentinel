import React, { useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';

export function ReconstructionChart({ events }) {
  
  const data = useMemo(() => {
    // Reverse events to chronological for chart, take last 60
    return [...events].reverse().slice(-60).map(e => ({
      time: e.timestamp.split("T")[1].substring(0, 8),
      sensor_ae: e.stream === 'sensor' ? e.ae_score : null,
      financial_ae: e.stream === 'financial' ? e.ae_score : null,
    }));
  }, [events]);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis 
            dataKey="time" 
            stroke="var(--text-muted)" 
            tick={{fontSize: 10, fill: 'var(--text-muted)'}} 
            minTickGap={30}
          />
          <YAxis 
            stroke="var(--text-muted)" 
            tick={{fontSize: 10, fill: 'var(--text-muted)'}}
            domain={[0, 1.2]}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '4px' }}
            itemStyle={{ color: 'var(--text-primary)' }}
          />
          
          <ReferenceLine y={1.0} stroke="var(--severity-medium)" strokeDasharray="3 3" label={{ position: 'top', value: 'Threshold', fill: 'var(--severity-medium)', fontSize: 10 }} />
          
          <Line 
            type="monotone" 
            dataKey="sensor_ae" 
            stroke="var(--accent-normal)" 
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
            connectNulls
          />
          <Line 
            type="monotone" 
            dataKey="financial_ae" 
            stroke="#A855F7" // Purple
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
