import torch
import os
from inference import RULPredictor

def create_model():
    model = RULPredictor()
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    path = os.path.join(models_dir, "model_M01.pth")
    torch.save(model.state_dict(), path)
    print(f"Dummy model saved to {path}")

if __name__ == "__main__":
    create_model()
