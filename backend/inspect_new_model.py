import torch
import os

model_path = r"c:\Users\Алексей\Desktop\обучение\model_M01.pth"
if os.path.exists(model_path):
    sd = torch.load(model_path, map_location='cpu')
    print("Keys in state_dict:")
    for k in list(sd.keys())[:15]:
        print(f"  {k}: {sd[k].shape}")
else:
    print("File not found")
