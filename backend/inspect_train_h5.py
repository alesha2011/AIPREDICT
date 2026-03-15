import pandas as pd
import h5py
import os

file_path = r"c:\Users\Алексей\Desktop\обучение\LOGS\M02\M02_Aug_2019_OP01_000.h5"

print(f"File: {file_path}")
print(f"Exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    try:
        with h5py.File(file_path, 'r') as f:
            print(f"Keys: {list(f.keys())}")
            for k in f.keys():
                data = f[k][:]
                print(f"  Key '{k}' shape: {data.shape}")
                print(f"  Key '{k}' first row: {data[0]}")
    except Exception as e:
        print(f"Error reading with h5py: {e}")

    try:
        df = pd.read_hdf(file_path)
        print("Successfully read with pd.read_hdf()")
        print(f"Columns: {list(df.columns)}")
        print(f"Head:\n{df.head()}")
    except Exception as e:
        print(f"Error reading with pd.read_hdf(): {e}")
