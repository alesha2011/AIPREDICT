import torch
import torch.nn as nn
import os
import numpy as np

# Default dummy model for fallback
class RULPredictor(nn.Module):
    def __init__(self):
        super(RULPredictor, self).__init__()
        self.fc1 = nn.Linear(4, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 1)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# High-accuracy model from training
class AdvancedCNCModel(nn.Module):
    def __init__(self):
        super(AdvancedCNCModel, self). __init__()
        self.features = nn.Sequential(
            nn.Conv1d(3, 64, kernel_size=7, padding=3, stride=2),
            nn.BatchNorm1d(64),
            nn.LeakyReLU(0.2),
            nn.MaxPool1d(2),

            nn.Conv1d(64, 128, kernel_size=5, padding=2),
            nn.BatchNorm1d(128),
            nn.LeakyReLU(0.2),
            nn.MaxPool1d(2),

            nn.Conv1d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2),
            nn.AdaptiveAvgPool1d(32)
        )

        self.lstm = nn.LSTM(input_size=256, hidden_size=128, batch_first=True, num_layers=2, dropout=0.3)

        self.fc = nn.Sequential(
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(64, 1)
        )

    def forward(self, x_vib):
        # x_vib expected shape: [Batch, 1024, 3] or [Batch, Seq, 3]
        x = x_vib.permute(0, 2, 1) # [Batch, 3, 1024]
        x = self.features(x)
        x = x.permute(0, 2, 1) # [Batch, 32, 256]
        _, (hn, _) = self.lstm(x)
        out = self.fc(hn[-1])
        return out

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
_model_cache = {}

def get_model(machine_id: str):
    global _model_cache
    
    machine_id = machine_id.replace("/", "").replace("\\", "").replace(".", "")
    model_path = os.path.join(MODEL_DIR, f"model_{machine_id}.pth")
    
    if machine_id in _model_cache:
        return _model_cache[machine_id]
    
    if os.path.exists(model_path):
        try:
            # Use weights_only=False because LSTM/BN might need it, though strictly not for state_dict
            state_dict = torch.load(model_path, map_location='cpu')
            
            # Detect architecture
            if "features.0.weight" in state_dict:
                print(f"Detected AdvancedCNCModel for {machine_id}")
                model = AdvancedCNCModel()
                model.load_state_dict(state_dict)
            elif "weight" in state_dict and "bias" in state_dict and "fc1.weight" not in state_dict:
                out_features, in_features = state_dict["weight"].shape
                print(f"Detected simple Linear model for {machine_id} ({in_features} -> {out_features})")
                model = nn.Linear(in_features, out_features)
                model.load_state_dict(state_dict)
            else:
                model = RULPredictor()
                model.load_state_dict(state_dict)
            
            model.eval()
            print(f"Loaded model for {machine_id} from {model_path}")
            _model_cache[machine_id] = model
            return model
        except Exception as e:
            print(f"Error loading model for {machine_id}: {e}. Using dummy.")
    
    model = RULPredictor()
    model.eval()
    return model

def predict_rul(sensor_data: list, machine_id: str = "M01") -> float:
    """
    Predicts RUL. 
    sensor_data can be:
    - list[float] (length 4) for simple models
    - list[list[float]] or np.array (shape N x 3) for Advanced model
    """
    model = get_model(machine_id)
    model.eval()
    
    with torch.no_grad():
        if isinstance(model, AdvancedCNCModel):
            # Input shape [1, 1024, 3]
            data = np.array(sensor_data, dtype=np.float32)
            if len(data.shape) == 1: # Fallback if someone passed 1D data
                data = data.reshape(-1, 3)
            
            # Pad to 1024 if needed
            if data.shape[0] < 1024:
                pad = np.zeros((1024 - data.shape[0], 3), dtype=np.float32)
                data = np.vstack((data, pad))
            else:
                data = data[:1024, :3]
            
            # Normalization (Mean subtraction as in training)
            mean = np.mean(data, axis=0, keepdims=True)
            data = data - mean
            
            input_tensor = torch.tensor(data).unsqueeze(0)
            prediction = model(input_tensor)
        else:
            # Simple model expects [Batch, Features]
            features = list(sensor_data)
            expected = 4
            if isinstance(model, nn.Linear): expected = model.in_features
            elif hasattr(model, 'fc1'): expected = model.fc1.in_features
            
            if len(features) < expected:
                features.extend([0.0] * (expected - len(features)))
            input_tensor = torch.tensor([features[:expected]], dtype=torch.float32)
            prediction = model(input_tensor)
            
        return max(0.0, float(prediction.item()))
