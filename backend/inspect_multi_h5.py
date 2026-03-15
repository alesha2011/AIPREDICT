import pandas as pd
import h5py
import os

base_dir = r"c:\Users\Алексей\Desktop\обучение\LOGS\M02"
files = os.listdir(base_dir)

for f_name in files[:5]:
    file_path = os.path.join(base_dir, f_name)
    print(f"\nAnalyzing: {f_name}")
    try:
        with h5py.File(file_path, 'r') as f:
            keys = list(f.keys())
            print(f"  Keys: {keys}")
            for k in keys:
                data = f[k][:]
                print(f"    Key '{k}' shape: {data.shape}")
                # Try to read with pandas
                try:
                    df = pd.read_hdf(file_path, key=k)
                    print(f"    Key '{k}' read with pandas. Columns: {list(df.columns)}")
                except:
                    print(f"    Key '{k}' NOT readable with pandas.")
    except Exception as e:
        print(f"  Error: {e}")
