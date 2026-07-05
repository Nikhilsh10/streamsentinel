import asyncio
import time
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .db.database import init_db
from .websocket.manager import ConnectionManager
from .consumer.kafka_consumer import kafka_consumer_loop
from .ml.preprocessor import load_models
from .api.routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.start_time = time.time()
    
    if_w = app.state.if_weight
    ae_w = app.state.ae_weight
    if abs(if_w + ae_w - 1.0) > 1e-6:
        raise ValueError(
            f"IF_WEIGHT ({if_w}) + AE_WEIGHT ({ae_w}) must equal 1.0. "
            f"Current sum: {if_w + ae_w}. Check your .env file."
        )
    
    # Initialize DB
    await init_db()
    
    # Load Models
    await asyncio.to_thread(load_models, app.state)
    
    # Start Kafka Consumer Task
    consumer_task = asyncio.create_task(kafka_consumer_loop(app.state))
    
    yield
    
    # Shutdown
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="StreamSentinel API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AppState
app.state.ws_manager = ConnectionManager()
app.state.event_counter = 0
app.state.anomaly_counter = 0
app.state.recent_latencies = deque(maxlen=1000)
app.state.fusion_threshold = settings.FUSION_THRESHOLD
app.state.if_weight = settings.IF_WEIGHT
app.state.ae_weight = settings.AE_WEIGHT
app.state.events_per_second = 0.0

app.include_router(api_router, prefix="/api")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await app.state.ws_manager.connect(websocket)
    try:
        while True:
            # We don't really expect clients to send data, but we can handle threshold updates if needed
            data = await websocket.receive_text()
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        app.state.ws_manager.disconnect(websocket)
