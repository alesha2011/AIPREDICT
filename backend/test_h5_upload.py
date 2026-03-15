import pandas as pd
import numpy as np
import os
import requests

# 1. Create a dummy H5 file
df = pd.DataFrame({
    'sensor_1': np.random.randn(10),
    'sensor_2': np.random.randn(10),
    'sensor_3': np.random.randn(10),
    'sensor_4': np.random.randn(10)
})

h5_path = 'test_data.h5'
try:
    df.to_hdf(h5_path, key='data', mode='w')
    print(f"Created {h5_path}")
except Exception as e:
    print(f"Error creating H5: {e}")
    exit(1)

# 2. Try to upload to local server
url = 'http://localhost:8000/api/v1/upload-logs?machine_id=M01&is_dataset=false'
try:
    with open(h5_path, 'rb') as f:
        files = {'file': (h5_path, f, 'application/x-hdf5')}
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Request error: {e}")

if os.path.exists(h5_path):
    os.remove(h5_path)
