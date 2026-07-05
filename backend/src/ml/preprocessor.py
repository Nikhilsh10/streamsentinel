import joblib
import torch
import torch.nn as nn
import json

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

def load_models(app_state):
    print("Loading models...")
    try:
        # Load Sensor Models
        app_state.if_sensor = joblib.load("/app/models/if_sensor.joblib")
        app_state.scaler_sensor = joblib.load("/app/models/scaler_sensor.joblib")
        
        app_state.ae_sensor = Autoencoder(4)
        app_state.ae_sensor.load_state_dict(torch.load("/app/models/ae_sensor.pth"))
        app_state.ae_sensor.eval()
        
        with open("/app/models/ae_sensor_meta.json", "r") as f:
            app_state.ae_sensor_meta = json.load(f)
            
        # Load Financial Models
        app_state.if_financial = joblib.load("/app/models/if_financial.joblib")
        app_state.scaler_financial = joblib.load("/app/models/scaler_financial.joblib")
        
        app_state.ae_financial = Autoencoder(3)
        app_state.ae_financial.load_state_dict(torch.load("/app/models/ae_financial.pth"))
        app_state.ae_financial.eval()
        
        with open("/app/models/ae_financial_meta.json", "r") as f:
            app_state.ae_financial_meta = json.load(f)
            
        print("Models loaded successfully.")
    except Exception as e:
        raise RuntimeError(
            f"Failed to load ML models. Run 'make train' first. Error: {e}"
        ) from e
