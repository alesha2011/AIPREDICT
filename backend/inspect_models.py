import torch
import os

model_dir = r"c:\Users\Алексей\Desktop\обучение\predictive-maintenance\backend\ml\models"
for m in ["M01", "M02", "M03"]:
    p = os.path.join(model_dir, f"model_{m}.pth")
    if os.path.exists(p):
        print(f"\nModel {m}:")
        try:
            sd = torch.load(p, weights_only=True)
            for k, v in sd.items():
                print(f"  {k}: {v.shape}")
        except Exception as e:
            print(f"  Error: {e}")
