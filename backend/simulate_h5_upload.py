import pandas as pd
import h5py
import numpy as np
import os

# --- MOCKED logic from routes.py ---

def normalize_sensor_columns(df):
    cols_lower = {str(c).lower(): c for c in df.columns}
    for p in ['s1', 's2', 's3', 's4', '0', '1', '2']:
        if p in cols_lower:
            return df
    if len(df.columns) >= 3:
        df = df.copy()
        df.columns = [str(c) for c in df.columns]
        num_cols = min(len(df.columns), 4)
        first_cols = list(df.columns)[:num_cols]
        rename = {first_cols[i]: f's{i+1}' for i in range(num_cols)}
        df = df.rename(columns=rename)
    return df

processed_count = 0

def process_dataframe(df, source_name):
    global processed_count
    df = normalize_sensor_columns(df)
    cols = {str(c).lower(): c for c in df.columns}
    print(f"Normalized columns: {list(df.columns)}")
    print(f"Cols mapping dict: {cols}")
    
    s_maps = []
    for i in range(1, 5):
        found = False
        for p in [f's{i}', f'sensor_{i}', f'sensor{i}', f'vibration_{i}', str(i-1)]:
            if p in cols:
                s_maps.append(cols[p])
                found = True
                break
        if not found:
            if i == 4:
                s_maps.append(None)
            else:
                print(f"Warning: Sensor {i} not found in columns: {list(df.columns)}")
                return
    
    print(f"Sensor maps: {s_maps}")
    
    for _, row in df.iterrows():
        try:
            sensors = []
            for c in s_maps:
                if c is None:
                    sensors.append(0.0)
                else:
                    sensors.append(float(row[c]))
            
            # (In reality we call predict_rul here)
            processed_count += 1
        except Exception as e:
            print(f"Row processing failed: {e}")
            continue

# --- Simulation ---

file_path = r"c:\Users\Алексей\Desktop\обучение\LOGS\M02\M02_Aug_2019_OP01_000.h5"

if os.path.exists(file_path):
    print(f"Simulating processing for {file_path}")
    df = None
    try:
        with h5py.File(file_path, 'r') as f:
            keys = list(f.keys())
            for k in keys:
                print(f"Trying key: {k}")
                # Manual fallback logic
                data = f[k][:]
                df = pd.DataFrame(data)
                
                # Logic from H5 branch in routes.py
                if df.shape[1] >= 4:
                    if all(isinstance(c, int) for c in df.columns):
                        df.columns = [f's{i+1}' for i in range(df.shape[1])]
                
                if df is not None and not df.empty:
                    print(f"Found valid DataFrame for key {k}")
                    process_dataframe(df, "Simulation")
                    break
    except Exception as e:
        print(f"Simulation failed: {e}")

    print(f"Total processed: {processed_count}")
else:
    print("File not found")
