import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

def train_if_model(stream):
    print(f"Training Isolation Forest for {stream}...")
    
    df = pd.read_parquet(f"data/{stream}_train.parquet")
    
    # Feature selection
    if stream == "sensor":
        features = ["temperature", "vibration", "pressure", "current_draw"]
    else:
        features = ["amount", "hour_of_day", "velocity_30s"]
        
    X = df[features].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = IsolationForest(n_estimators=200, contamination=0.05, random_state=42)
    model.fit(X_scaled)
    
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, f"models/if_{stream}.joblib")
    joblib.dump(scaler, f"models/scaler_{stream}.joblib")
    print(f"Saved models/if_{stream}.joblib and models/scaler_{stream}.joblib")

if __name__ == "__main__":
    train_if_model("sensor")
    train_if_model("financial")
