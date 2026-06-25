import aiosqlite
import json
import os
from .models import ScoredEvent
from ..config import settings

async def init_db():
    os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS anomalies (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id        TEXT NOT NULL UNIQUE,
                stream          TEXT NOT NULL CHECK(stream IN ('sensor', 'financial')),
                device_or_user  TEXT,
                timestamp       TEXT NOT NULL,
                if_score        REAL NOT NULL,
                ae_score        REAL NOT NULL,
                fusion_score    REAL NOT NULL,
                severity        TEXT NOT NULL CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH')),
                raw_features    TEXT NOT NULL,
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp DESC);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_stream ON anomalies(stream, timestamp DESC);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);")
        await db.commit()

async def insert_anomaly(event: ScoredEvent):
    device_or_user = event.features.get("device_id") or event.features.get("user_id")
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute(
            """INSERT INTO anomalies 
            (event_id, stream, device_or_user, timestamp, if_score, ae_score, fusion_score, severity, raw_features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event.event_id,
                event.stream,
                device_or_user,
                event.timestamp.isoformat(),
                event.if_score,
                event.ae_score,
                event.fusion_score,
                event.severity,
                json.dumps(event.features)
            )
        )
        await db.commit()

async def get_recent_anomalies(limit: int = 50, stream: str = None):
    query = "SELECT id, event_id, stream, timestamp, fusion_score, severity, raw_features FROM anomalies"
    params = []
    if stream:
        query += " WHERE stream = ?"
        params.append(stream)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    async with aiosqlite.connect(settings.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
