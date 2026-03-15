import torch
import sys
import os

# Add the current directory to sys.path to import ml.inference
sys.path.append(os.getcwd())

from ml.inference import predict_rul, get_model

def test_robust_loading():
    print("Testing robust model loading...")
    
    # Test M02 (which has the simple Linear(10, 1) structure)
    try:
        model = get_model("M02")
        print(f"Model M02 type: {type(model)}")
        
        # Test prediction with 4 features (should be padded to 10)
        features = [1.0, 2.0, 3.0, 4.0]
        rul = predict_rul(features, machine_id="M02")
        print(f"Prediction for M02: {rul}")
        
        if rul >= 0:
            print("SUCCESS: Correctly handled architecture mismatch and padding for M02")
        else:
            print("FAILURE: Prediction returned negative value")
            
    except Exception as e:
        print(f"FAILURE: Exception during M02 test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_robust_loading()
