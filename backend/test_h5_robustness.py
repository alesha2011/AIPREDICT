import pandas as pd
import numpy as np
import h5py
import os
import tempfile
import io

def test_h5_reading_logic():
    # 1. Create a "Pandas" H5 file
    pandas_h5 = "test_pandas.h5"
    df_orig = pd.DataFrame({
        's1': np.random.randn(10),
        's2': np.random.randn(10),
        's3': np.random.randn(10),
        's4': np.random.randn(10)
    })
    df_orig.to_hdf(pandas_h5, key='vibration_data', mode='w')
    
    # 2. Create a "Raw" H5 file
    raw_h5 = "test_raw.h5"
    with h5py.File(raw_h5, 'w') as f:
        f.create_dataset('data', data=np.random.randn(10, 4))
    
    files_to_test = [pandas_h5, raw_h5]
    
    success_count = 0
    for file_path in files_to_test:
        print(f"\nTesting file: {file_path}")
        df = None
        error_log = []
        
        # Simulated logic from routes.py
        try:
            df = pd.read_hdf(file_path)
            print("  Read successfully with pd.read_hdf(auto)")
        except Exception as e:
            error_log.append(f"pd.read_hdf(auto) failed: {str(e)}")
            
        if df is None:
            try:
                with h5py.File(file_path, 'r') as f:
                    keys = list(f.keys())
                    print(f"  Keys found: {keys}")
                    if keys:
                        for k in keys:
                            try:
                                # Attempt 1: pandas read_hdf
                                try:
                                    df = pd.read_hdf(file_path, key=k)
                                    print(f"  Read successfully with pd.read_hdf(key={k})")
                                except Exception:
                                    df = None
                                
                                # Attempt 2: manual dataset extraction if pandas fails
                                if df is None:
                                    data = f[k][:]
                                    df = pd.DataFrame(data)
                                    if df.shape[1] >= 4:
                                        if all(isinstance(c, int) for c in df.columns):
                                            df.columns = [f's{i+1}' for i in range(df.shape[1])]
                                    print(f"  Read successfully with manual fallback for key={k}")
                                
                                if df is not None and not df.empty:
                                    break
                            except Exception as e:
                                error_log.append(f"Reading key={k} failed: {str(e)}")
            except Exception as e:
                error_log.append(f"h5py fallback failed: {str(e)}")

        if df is not None:
            print(f"  Final DataFrame shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            success_count += 1
        else:
            print(f"  FAILED to read {file_path}")
            print(f"  Errors: {error_log}")

    # Cleanup
    for f in files_to_test:
        if os.path.exists(f): os.remove(f)
        
    if success_count == len(files_to_test):
        print("\nALL TESTS PASSED")
    else:
        print(f"\nTESTS FAILED: {success_count}/{len(files_to_test)} passed")

if __name__ == "__main__":
    test_h5_reading_logic()
