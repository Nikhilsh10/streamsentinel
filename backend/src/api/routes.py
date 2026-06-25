from fastapi import APIRouter, Request, HTTPException
from typing import List
from ..db.database import get_recent_anomalies
from ..db.models import HealthResponse, MetricsResponse, AnomalyRecord
import numpy as np

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    app_state = request.app.state
    uptime = (request.app.state.start_time - np.datetime64('now')).astype(float) * -1 # simplified
    return {
        "status": "ok",
        "kafka_connected": True, # Simplification
        "models_loaded": {
            "if_sensor": hasattr(app_state, "if_sensor"),
            "ae_sensor": hasattr(app_state, "ae_sensor")
        },
        "anomaly_count_24h": app_state.anomaly_counter,
        "uptime_seconds": 0.0 # replace with actual
    }

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(request: Request):
    app_state = request.app.state
    latencies = list(app_state.recent_latencies)
    p95_latency = float(np.percentile(latencies, 95)) if latencies else 0.0
    
    # eps calculation would need a time window, stubbed for now
    eps = app_state.events_per_second 
    
    rate = (app_state.anomaly_counter / max(1, app_state.event_counter)) * 100
    
    return {
        "events_per_second": eps,
        "anomaly_rate_pct": rate,
        "avg_fusion_score": 0.0, # Stub
        "avg_latency_ms": p95_latency,
        "total_events": app_state.event_counter,
        "total_anomalies": app_state.anomaly_counter
    }

@router.get("/anomalies", response_model=List[dict])
async def get_anomalies(limit: int = 50, stream: str = None):
    return await get_recent_anomalies(limit, stream)

@router.post("/threshold")
async def update_threshold(request: Request, value: float):
    request.app.state.fusion_threshold = value
    return {"status": "success", "new_threshold": value}
