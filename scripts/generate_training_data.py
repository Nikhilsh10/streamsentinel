import os
import sys
import pandas as pd
import numpy as np

# Add producer/src to path to reuse the generator
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "producer", "src"))
from generator import generate_sensor_event, generate_financial_event

def generate_dataset(stream_type, num_samples, anomaly_rate=0.0):
    events = []
    for _ in range(num_samples):
        is_anomaly = (np.random.random() < anomaly_rate) if anomaly_rate > 0 else False
        anomaly_type = None
        
        if is_anomaly:
            if stream_type == "sensor":
                anomaly_type = np.random.choice(['point', 'contextual'])
            else:
                anomaly_type = np.random.choice(['point', 'collective'])
                
        if stream_type == "sensor":
            events.append(generate_sensor_event(anomaly_type))
        else:
            events.append(generate_financial_event(anomaly_type))
            
    return pd.DataFrame(events)

if __name__ == "__main__":
    
    os.makedirs("data", exist_ok=True)
    
    print("Generating sensor training data (normal only)...")
    sensor_train = generate_dataset("sensor", 50000, anomaly_rate=0.0)
    sensor_train.to_parquet("data/sensor_train.parquet")
    
    print("Generating sensor eval data (5% anomalies)...")
    sensor_eval = generate_dataset("sensor", 2500, anomaly_rate=0.05)
    sensor_eval.to_parquet("data/sensor_eval.parquet")
    
    print("Generating financial training data (normal only)...")
    fin_train = generate_dataset("financial", 50000, anomaly_rate=0.0)
    fin_train.to_parquet("data/financial_train.parquet")
    
    print("Generating financial eval data (5% anomalies)...")
    fin_eval = generate_dataset("financial", 2500, anomaly_rate=0.05)
    fin_eval.to_parquet("data/financial_eval.parquet")
    
    print("Data generation complete.")
