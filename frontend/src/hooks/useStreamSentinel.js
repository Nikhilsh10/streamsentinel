import { useState, useEffect, useRef, useCallback } from 'react';

export function useStreamSentinel(url) {
  const [events, setEvents] = useState([]);
  const [metrics, setMetrics] = useState({ eps: 0, anomalyRate: 0 });
  const [status, setStatus] = useState('connecting'); // connecting, connected, disconnected
  const wsRef = useRef(null);
  const reconnectDelay = useRef(1000);
  
  // Rolling metrics calculation
  const metricsData = useRef({
    count: 0,
    anomalies: 0,
    startTime: Date.now()
  });

  const connect = useCallback(() => {
    setStatus('connecting');
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      const event = JSON.parse(e.data);
      
      setEvents(prev => {
        const newEvents = [event, ...prev];
        return newEvents.slice(0, 200);
      });
      
      // Update metrics
      metricsData.current.count += 1;
      if (event.is_anomaly) metricsData.current.anomalies += 1;
      
      const now = Date.now();
      const elapsed = (now - metricsData.current.startTime) / 1000;
      
      if (elapsed > 2) {
        setMetrics({
          eps: (metricsData.current.count / elapsed).toFixed(1),
          anomalyRate: ((metricsData.current.anomalies / metricsData.current.count) * 100).toFixed(1)
        });
        // reset every 10s roughly
        if (elapsed > 10) {
            metricsData.current = { count: 0, anomalies: 0, startTime: now };
        }
      }
    };

    ws.onclose = () => {
      setStatus('disconnected');
      setTimeout(() => {
        reconnectDelay.current = Math.min(reconnectDelay.current * 2, 30000);
        connect();
      }, reconnectDelay.current);
    };

    ws.onopen = () => { 
      setStatus('connected');
      reconnectDelay.current = 1000; 
    };
  }, [url]);

  useEffect(() => { 
    connect(); 
    return () => wsRef.current?.close(); 
  }, [connect]);
  
  return { events, metrics, status };
}
