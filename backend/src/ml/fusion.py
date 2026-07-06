import time
import torch
import numpy as np
from datetime import datetime
from ..db.models import ScoredEvent
from ..config import settings

def normalize_if_score(scores):
    scores = -scores  # invert: higher = more anomalous
    # Calibrated to actual IsolationForest score_samples output range:
    # Normal events: raw ~[-0.75, -0.45] → inverted [0.45, 0.75]
    # Anomalies:     raw < -0.75         → inverted > 0.75
    # Map [0.4, 0.9] → [0, 1] so normal events score ~0.1-0.7,
    # only genuine outliers push near 1.0.
    norm = (scores - 0.4) / (0.9 - 0.4)
    return np.clip(norm, 0, 1)

async def score_event(app_state, event_data: dict) -> ScoredEvent:
    t0 = time.monotonic()
    stream = event_data["stream"]
    
    if stream == "sensor":
        features = ["temperature", "vibration", "pressure", "current_draw"]
        if_model = app_state.if_sensor
        scaler = app_state.scaler_sensor
        ae_model = app_state.ae_sensor
        ae_meta = app_state.ae_sensor_meta
    else:
        features = ["amount", "hour_of_day", "velocity_30s"]
        if_model = app_state.if_financial
        scaler = app_state.scaler_financial
        ae_model = app_state.ae_financial
        ae_meta = app_state.ae_financial_meta

    # Extract feature array
    X = np.array([[event_data[f] for f in features]])
    
    # Scale
    X_scaled = scaler.transform(X)
    
    # IF Inference
    if_raw = if_model.score_samples(X_scaled)
    if_score = float(normalize_if_score(if_raw)[0])
    
    # AE Inference
    with torch.no_grad():
        X_tensor = torch.FloatTensor(X_scaled)
        pred = ae_model(X_tensor)
        mse = torch.mean((pred - X_tensor)**2, dim=1).numpy()[0]
        
    ae_score = float(np.clip(mse / (ae_meta["threshold"] * 1.5), 0, 1))
    
    # Fusion
    fusion_score = app_state.if_weight * if_score + app_state.ae_weight * ae_score
    
    if fusion_score >= 0.85:
        severity = "HIGH"
    elif fusion_score >= 0.65:
        severity = "MEDIUM"
    elif fusion_score >= 0.45:
        severity = "LOW"
    else:
        severity = "NORMAL"
        
    is_anomaly = fusion_score >= app_state.fusion_threshold
    
    latency = (time.monotonic() - t0) * 1000
    app_state.recent_latencies.append(latency)
    
    return ScoredEvent(
        event_id=event_data["event_id"],
        stream=stream,
        timestamp=datetime.fromisoformat(event_data["timestamp"]),
        features=event_data,
        if_score=if_score,
        ae_score=ae_score,
        fusion_score=fusion_score,
        severity=severity,
        is_anomaly=is_anomaly,
        inference_latency_ms=latency
    )
