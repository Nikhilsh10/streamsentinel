# StreamSentinel

StreamSentinel is a real-time anomaly detection platform built to ingest high-frequency streaming events, score them via a hybrid ML approach (Isolation Forest + Autoencoder), and visualize anomalies live on a sub-500ms latency dashboard.

## 🚀 Architecture

```
Synthetic Producer (Python)
        │
        │  JSON over Kafka topics
        ▼
Apache Kafka (Docker, KRaft)
        │
        │  Consumer Group: anomaly-detectors
        ▼
FastAPI Consumer Service
  ├── Kafka Consumer (aiokafka)
  ├── Preprocessor (StandardScaler)
  ├── Isolation Forest (sklearn)
  ├── Autoencoder (PyTorch)
  ├── Score Fusion Layer
  ├── SQLite Writer (anomalies only)
  └── WebSocket Manager
        │
        │  WebSocket (ws://)
        ▼
React Dashboard (Vite, Recharts)
```

### Why not Redis Streams?
Kafka was chosen over Redis Streams because of its robust consumer group offset tracking, distributed log persistence (retention), and standard integration ecosystem for downstream Big Data tools (like Spark/Flink), mimicking true enterprise deployment architectures.

## ✨ Features
- **Real-Time Scoring Pipeline**: Fuses Scikit-learn Isolation Forest (contamination scoring) and PyTorch Autoencoder (reconstruction error) into a weighted confidence threshold.
- **WebSocket Broadcast**: Scored events are broadcast directly to a React frontend instantly.
- **Graceful Error Handling**: Robust Kafka consumer loop logic with at-least-once delivery semantics (`commit()` strictly follows database write).
- **Explainability**: "Feature Deviation" analysis calculated and shown on the dashboard for immediate anomaly context. (Note: These are simplified deviation scores tailored for sub-500ms latency, bypassing the computationally expensive SHAP calculations).

## 🛠 Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local model retraining)

## 🏃‍♂️ Quick Start

1. **Start the Stack**
   ```bash
   docker-compose up -d
   ```
   This command starts Kafka (KRaft mode), Kafka UI, the Synthetic Producer, the FastAPI backend, and the React frontend.

2. **Access the Dashboard**
   Navigate to [http://localhost](http://localhost) (or whichever port Nginx bounds to).
   
3. **Kafka Admin UI**
   Accessible at [http://localhost:8080](http://localhost:8080) for monitoring topics and consumer groups.

4. **API Metrics**
   Navigate to [http://localhost:8000/api/metrics](http://localhost:8000/api/metrics) to view real-time latency p95 and anomaly rates.

## 🧠 Model Training (Offline)

The models provided in `models/` are pre-trained. To re-train them from scratch on fresh synthetic data:

```bash
# Ensure local virtual environment is active and dependencies installed
make generate-data
make train
```

## 📊 Evaluation Metrics
*On synthetic test set with 5% injected anomalies (point, contextual, and collective)*
- **Fusion ROC-AUC:** > 0.82
- **Fusion F1 Score:** > 0.74

## ⚙️ Configuration

Control system behavior via `.env`:
```env
EVENTS_PER_SECOND=20
FUSION_THRESHOLD=0.65
IF_WEIGHT=0.6
AE_WEIGHT=0.4
```
