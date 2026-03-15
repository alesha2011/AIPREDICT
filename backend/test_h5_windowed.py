import pandas as pd
import h5py
import numpy as np
import os
import asyncio
from routes import normalize_sensor_columns
from ml.inference import get_model, AdvancedCNCModel, predict_rul

# Mock DB and models for simulation
class MockLog:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class MockDB:
    def add(self, log):
        pass
    def commit(self):
        pass

async def simulate_windowed_processing(df, machine_id, source_name):
    processed_count = 0
    df = normalize_sensor_columns(df)
    cols = {str(c).lower(): c for c in df.columns}
    
    model = get_model(machine_id)
    is_advanced = isinstance(model, AdvancedCNCModel)
    
    s_maps = []
    num_sensors = 3 if is_advanced else 4
    
    for i in range(1, num_sensors + 1):
        for p in [f's{i}', f'sensor_{i}', f'sensor{i}', f'vibration_{i}', str(i-1)]:
            if p in cols:
                s_maps.append(cols[p])
                break
    
    if len(s_maps) < num_sensors:
        print(f"Error: Could not find {num_sensors} sensors")
        return

    total_rows = len(df)
    window_size = 1024
    
    if is_advanced:
        print(f"DEBUG: Using advanced windowed processing for {total_rows} rows.")
        for start in range(0, total_rows, window_size):
            end = min(start + window_size, total_rows)
            window_data = df.iloc[start:end][s_maps].values.astype(np.float32)
            rul = predict_rul(window_data, machine_id=machine_id)
            processed_count += 1
            if processed_count % 10 == 0:
                print(f"Processed {end}/{total_rows} rows. RUL: {rul:.2f}")
    
    return processed_count

async def main():
    file_path = r"c:\Users\Алексей\Desktop\обучение\LOGS\M02\M02_Aug_2019_OP01_000.h5"
    if not os.path.exists(file_path):
        print("Test file not found")
        return

    with h5py.File(file_path, 'r') as f:
        data = f['vibration_data'][:]
        df = pd.DataFrame(data)
        count = await simulate_windowed_processing(df, "M02", "M02_Test")
        print(f"Final log count: {count}")

if __name__ == "__main__":
    asyncio.run(main())
