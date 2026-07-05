from dataclasses import dataclass
from collections import deque
from typing import Any, Optional

@dataclass
class AppState:
    start_time: float = 0.0
    ws_manager: Any = None
    event_counter: int = 0
    anomaly_counter: int = 0
    recent_latencies: deque = None
    fusion_threshold: float = 0.65
    if_weight: float = 0.6
    ae_weight: float = 0.4
    events_per_second: float = 0.0
    
    if_sensor: Any = None
    scaler_sensor: Any = None
    ae_sensor: Any = None
    ae_sensor_meta: dict = None
    
    if_financial: Any = None
    scaler_financial: Any = None
    ae_financial: Any = None
    ae_financial_meta: dict = None

    def __post_init__(self):
        if self.recent_latencies is None:
            self.recent_latencies = deque(maxlen=1000)
