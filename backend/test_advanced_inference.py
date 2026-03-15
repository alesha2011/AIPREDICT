import torch
import numpy as np
from ml.inference import predict_rul, get_model, AdvancedCNCModel

def test_advanced_loading():
    print("Testing AdvancedCNCModel loading...")
    model = get_model("M01")
    if isinstance(model, AdvancedCNCModel):
        print("SUCCESS: Loaded AdvancedCNCModel for M01")
    else:
        print(f"FAILURE: Loaded {type(model)} instead of AdvancedCNCModel")

def test_advanced_prediction():
    print("\nTesting AdvancedCNCModel prediction...")
    # Mock window: 1024 samples, 3 sensors
    window = np.random.randn(1024, 3).tolist()
    
    rul = predict_rul(window, machine_id="M01")
    print(f"Prediction for M01: {rul:.2f}")
    
    if rul >= 0:
        print("SUCCESS: Prediction returned valid non-negative value")
    else:
        print(f"FAILURE: Prediction returned invalid value {rul}")

if __name__ == "__main__":
    test_advanced_loading()
    test_advanced_prediction()
