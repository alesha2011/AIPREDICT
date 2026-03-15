import pandas as pd
import numpy as np
import h5py
import os
import sys

# Add backend to path to import routes and stuff if needed, 
# but we'll simulate the logic here since we want to test the ALGORITHM
# the algorithm was copied into routes.py

def test_3column_h5_logic():
    test_file = "test_3col.h5"
    
    # 1. Create a file mimicking the user's screenshot
    # 3 columns (0, 1, 2), dataset name 'vibration_data'
    data = np.random.randn(10, 3)
    with h5py.File(test_file, 'w') as f:
        f.create_dataset('vibration_data', data=data)
    
    print(f"Created {test_file} with shape {data.shape} and key 'vibration_data'")

    # 2. Simulate the logic from routes.py
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

    try:
        # Step A: Identify keys
        with h5py.File(test_file, 'r') as f:
            keys = list(f.keys())
            print(f"Keys found: {keys}")
            
            # Step B: Read dataset
            df = None
            for k in keys:
                # In routes.py we try pd.read_hdf first
                try:
                    # Simulation of the fallback logic
                    data_raw = f[k][:]
                    df = pd.DataFrame(data_raw)
                    print(f"Read key {k}, initial columns: {list(df.columns)}")
                    break
                except Exception as e:
                    print(f"Failed to read {k}: {e}")

            if df is not None:
                # Step C: Normalize
                df = normalize_sensor_columns(df)
                print(f"After normalization: {list(df.columns)}")
                
                # Step D: Map sensors (simulating process_dataframe loop start)
                cols = {str(c).lower(): c for c in df.columns}
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
                            raise ValueError(f"Sensor {i} not found")
                
                print(f"Sensor mapping: {s_maps}")
                
                # Step E: Process row (simulating sensors assembly)
                row = df.iloc[0]
                sensors = []
                for c in s_maps:
                    if c is None:
                        sensors.append(0.0)
                    else:
                        sensors.append(float(row[c]))
                
                # Padding check
                while len(sensors) < 4:
                    sensors.append(0.0)
                
                final_sensors = sensors[:4]
                print(f"Final sensor data for inference: {final_sensors}")
                
                if len(final_sensors) == 4 and final_sensors[3] == 0.0:
                    print("SUCCESS: Correctly handled 3-column data with padding!")
                else:
                    print(f"FAILURE: Unexpected sensor data length or padding: {final_sensors}")
            else:
                print("FAILURE: Could not read DataFrame")

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_3column_h5_logic()
