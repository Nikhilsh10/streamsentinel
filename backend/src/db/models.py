from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field

# Event models
class SensorEvent(BaseModel):
    event_id: str
    stream: Literal["sensor"]
    timestamp: datetime
    device_id: str
    temperature: float
    vibration: float
    pressure: float
    current_draw: float
    is_injected_anomaly: bool = False

class FinancialEvent(BaseModel):
    event_id: str
    stream: Literal["financial"]
    timestamp: datetime
    user_id: str
    amount: float
    merchant_category: str
    hour_of_day: int = Field(ge=0, le=23)
    velocity_30s: int = Field(ge=0)
    country_code: str
    is_injected_anomaly: bool = False

# Inference output
class ScoredEvent(BaseModel):
    event_id: str
    stream: str
    timestamp: datetime
    features: dict
    if_score: float
    ae_score: float
    fusion_score: float
    severity: Literal["NORMAL", "LOW", "MEDIUM", "HIGH"]
    is_anomaly: bool
    inference_latency_ms: float

# REST responses
class AnomalyRecord(BaseModel):
    id: int
    event_id: str
    stream: str
    timestamp: datetime
    fusion_score: float
    severity: str
    raw_features: dict

class HealthResponse(BaseModel):
    status: str
    kafka_connected: bool
    models_loaded: dict
    anomaly_count_24h: int
    uptime_seconds: float

class MetricsResponse(BaseModel):
    events_per_second: float
    anomaly_rate_pct: float
    avg_fusion_score: float
    avg_latency_ms: float
    total_events: int
    total_anomalies: int
