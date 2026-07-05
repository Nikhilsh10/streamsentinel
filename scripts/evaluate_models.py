import pandas as pd
import numpy as np
import joblib
import torch
import json
from sklearn.metrics import classification_report, roc_auc_score, f1_score, confusion_matrix
from train_autoencoder import Autoencoder

def normalize_if_score(scores):
    # Isolation forest returns negative values for anomalies, positive for normal
    # We want [0, 1] where 1 is anomaly
    # typical range is [-0.5, 0.5]
    # let's just map it: 1 - (scores + 0.5) roughly
    # Actually, sklearn IF score_samples gives negative anomaly scores. Lower = more anomalous.
    # We can negate them and scale.
    scores = -scores
    min_s, max_s = scores.min(), scores.max()
    if max_s > min_s:
        return (scores - min_s) / (max_s - min_s)
    return scores

def evaluate(stream):
    print(f"\nEvaluating {stream.upper()} models...")
    df = pd.read_parquet(f"data/{stream}_eval.parquet")
    
    if stream == "sensor":
        features = ["temperature", "vibration", "pressure", "current_draw"]
    else:
        features = ["amount", "hour_of_day", "velocity_30s"]
        
    X = df[features].values
    y_true = df["is_injected_anomaly"].astype(int).values
    
    # 1. Isolation Forest
    scaler = joblib.load(f"models/scaler_{stream}.joblib")
    if_model = joblib.load(f"models/if_{stream}.joblib")
    
    X_scaled = scaler.transform(X)
    if_scores_raw = if_model.score_samples(X_scaled)
    if_scores = normalize_if_score(if_scores_raw)
    
    # 2. Autoencoder
    with open(f"models/ae_{stream}_meta.json", "r") as f:
        meta = json.load(f)
        ae_threshold = meta["threshold"]
        
    ae_model = Autoencoder(len(features))
    ae_model.load_state_dict(torch.load(f"models/ae_{stream}.pth"))
    ae_model.eval()
    
    with torch.no_grad():
        val_pred = ae_model(torch.FloatTensor(X_scaled))
        ae_mse = torch.mean((val_pred - torch.FloatTensor(X_scaled))**2, dim=1).numpy()
        
    ae_scores = ae_mse / (ae_threshold * 1.5) # rough normalization
    ae_scores = np.clip(ae_scores, 0, 1)
    
    # 3. Fusion
    fusion_scores = 0.6 * if_scores + 0.4 * ae_scores
    y_pred = (fusion_scores >= 0.65).astype(int)
    
    auc = roc_auc_score(y_true, fusion_scores)
    f1 = f1_score(y_true, y_pred)
    
    print(f"Fusion ROC-AUC: {auc:.4f}")
    print(f"Fusion F1: {f1:.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred))
    
    if auc < 0.80 or f1 < 0.70:
        print("WARNING: Metrics below acceptable threshold (AUC > 0.80, F1 > 0.70)")

if __name__ == "__main__":
    evaluate("sensor")
    evaluate("financial")
