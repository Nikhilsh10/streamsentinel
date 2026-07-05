import os
import json
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import joblib

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32), nn.ReLU(),
            nn.Linear(32, 16),        nn.ReLU(),
            nn.Linear(16, 8),         nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(8, 16),         nn.ReLU(),
            nn.Linear(16, 32),        nn.ReLU(),
            nn.Linear(32, input_dim)
        )
        
    def forward(self, x):
        return self.decoder(self.encoder(x))

def train_ae_model(stream):
    print(f"Training Autoencoder for {stream}...")
    
    df = pd.read_parquet(f"data/{stream}_train.parquet")
    
    if stream == "sensor":
        features = ["temperature", "vibration", "pressure", "current_draw"]
    else:
        features = ["amount", "hour_of_day", "velocity_30s"]
        
    X = df[features].values
    scaler = joblib.load(f"models/scaler_{stream}.joblib")
    X_scaled = scaler.transform(X)
    
    # Split train/val for threshold calculation
    val_size = int(len(X_scaled) * 0.1)
    X_train, X_val = X_scaled[:-val_size], X_scaled[-val_size:]
    
    train_tensor = torch.FloatTensor(X_train)
    val_tensor = torch.FloatTensor(X_val)
    
    train_loader = DataLoader(TensorDataset(train_tensor, train_tensor), batch_size=256, shuffle=True)
    
    model = Autoencoder(len(features))
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    model.train()
    for epoch in range(30):
        total_loss = 0
        for data, _ in train_loader:
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, data)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if (epoch+1) % 10 == 0:
            print(f"Epoch {epoch+1}/30, Loss: {total_loss/len(train_loader):.4f}")
            
    # Calculate threshold on val set (95th percentile of reconstruction error)
    model.eval()
    with torch.no_grad():
        val_pred = model(val_tensor)
        mse = torch.mean((val_pred - val_tensor)**2, dim=1).numpy()
        threshold = float(np.percentile(mse, 95))
        
    print(f"{stream} Autoencoder threshold (95th pct): {threshold:.6f}")
    
    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), f"models/ae_{stream}.pth")
    with open(f"models/ae_{stream}_meta.json", "w") as f:
        json.dump({"threshold": threshold, "features": features}, f)
        
if __name__ == "__main__":
    train_ae_model("sensor")
    train_ae_model("financial")
