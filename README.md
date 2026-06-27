# 🛡️ StreamSentinel 

<div align="center">
  <p><strong>A Real-Time Anomaly Detection System for High-Frequency Data Streams</strong></p>
  <p>
    <a href="#-architecture">Architecture</a> •
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-model-training">Model Training</a>
  </p>
</div>

---

**StreamSentinel** is an end-to-end, real-time anomaly detection platform. It ingests high-frequency synthetic events, scores them via a hybrid ML approach (Isolation Forest + PyTorch Autoencoder), and visualizes anomalies live on a sub-500ms latency dashboard.

Built as a demonstration of production-grade ML engineering, it showcases how to bridge the gap between batch-trained models and real-time streaming inference.

## 🚀 Architecture

```text
Synthetic Producer (Python)
        │
        │  JSON over Kafka topics
        ▼
Apache Kafka (KRaft mode)
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
React Dashboard (Vite, Recharts, Pure CSS)
```

### Why Kafka over Redis Streams?
Kafka was chosen for its robust consumer group offset tracking, distributed log persistence (retention), and standard integration ecosystem for downstream Big Data tools (like Spark/Flink), mimicking true enterprise deployment architectures.

## ✨ Features

- **Real-Time Scoring Pipeline**: Fuses Scikit-learn **Isolation Forest** (contamination scoring) and PyTorch **Autoencoder** (reconstruction error) into a weighted confidence threshold.
- **WebSocket Broadcast**: Scored events are broadcast directly to a React frontend instantly.
- **Graceful Error Handling**: Robust Kafka consumer loop logic with at-least-once delivery semantics (`commit()` strictly follows database write).
- **Explainability**: "Feature Deviation" analysis calculated and shown on the dashboard for immediate anomaly context. 

## 🛠️ Prerequisites

- **Docker & Docker Compose** (Ensure Docker Desktop is running)
- **Node.js 20+** (For local frontend development)
- **Python 3.11+** (For offline model training)

## 🏃‍♂️ Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nikhilsh10/streamsentinel.git
   cd streamsentinel
   ```

2. **Start the Stack**
   ```bash
   docker-compose up -d
   ```
   *This command spins up Kafka, Kafka UI, the Synthetic Producer, the FastAPI backend inference server, and the React frontend.*

3. **Access the Dashboard**
   - **Main UI**: Navigate to [http://localhost](http://localhost) 
   - **Kafka Admin UI**: Navigate to [http://localhost:8080](http://localhost:8080) for monitoring topics and consumer groups.
   - **API Metrics**: View real-time latency p95 and anomaly rates at [http://localhost:8000/api/metrics](http://localhost:8000/api/metrics).

## 🧠 Model Training (Offline)

The models provided in `models/` are pre-trained on synthetic data. To re-train them from scratch:

```bash
# Ensure local virtual environment is active and dependencies installed
make generate-data
make train
```

## 📊 Evaluation Metrics

*Tested on a synthetic test set with 5% injected anomalies (point, contextual, and collective)*

### Sensor Model
- **Fusion ROC-AUC:** `0.9941`
- **Fusion F1 Score:** `0.8413`
- **Precision:** `0.75` | **Recall:** `0.97`

### Financial Model
- **Fusion ROC-AUC:** `0.9906`
- **Fusion F1 Score:** `0.7143`
- **Precision:** `0.56` | **Recall:** `0.99`

- **End-to-End Latency (p95):** `< 500ms`

## ⚙️ Configuration

Control system behavior via the `.env` file at the root of the project:
```env
EVENTS_PER_SECOND=20
FUSION_THRESHOLD=0.65
IF_WEIGHT=0.6
AE_WEIGHT=0.4
```

---
*Developed by [Nikhil Sharma](https://github.com/Nikhilsh10)*
