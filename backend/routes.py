from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from sqlalchemy.orm import Session
import database, models, schemas, crud
from ml.inference import predict_rul, get_model, AdvancedCNCModel
import pandas as pd
import io
import secrets
import os
import tempfile
import traceback
import h5py
import numpy as np

router = APIRouter()

# Middleware for API Key verification
def verify_api_key(x_api_key: str = Header(...), db: Session = Depends(database.get_db)):
    key_data = crud.validate_api_key(db, x_api_key)
    if not key_data:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return key_data

@router.post("/login", response_model=schemas.LoginResponse)
def login_user(login_data: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_username(db, username=login_data.username)
    if not user or not crud.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Simple session token; in a real app this should be a signed JWT
    token = secrets.token_urlsafe(32)
    return schemas.LoginResponse(token=token, username=user.username)

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@router.get("/apikeys", response_model=list[schemas.APIKeyResponse])
def get_my_keys(
    machine_id: int = None,
    x_user: str | None = Header(default=None),
    db: Session = Depends(database.get_db),
):
    owner = crud.get_or_create_user_by_name(db, username=x_user or "default_owner")
    return crud.get_api_keys(db, owner_id=owner.id, machine_id=machine_id)

@router.post("/apikeys/generate", response_model=schemas.APIKeyResponse)
def generate_key(
    req: schemas.APIKeyCreate,
    x_user: str | None = Header(default=None),
    db: Session = Depends(database.get_db),
):
    owner = crud.get_or_create_user_by_name(db, username=x_user or "default_owner")
    return crud.create_api_key(db, owner_id=owner.id, mode=req.mode, machine_id=req.machine_id)

@router.patch("/apikeys/{key_id}", response_model=schemas.APIKeyResponse)
def update_key(
    key_id: int,
    req: schemas.APIKeyUpdate,
    x_user: str | None = Header(default=None),
    db: Session = Depends(database.get_db),
):
    key = crud.update_api_key(db, key_id=key_id, mode=req.mode)
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
    return key

# Machine Routes
@router.get("/machines", response_model=list[schemas.MachineResponse])
def get_machines(
    x_user: str | None = Header(default=None),
    db: Session = Depends(database.get_db),
):
    owner = crud.get_or_create_user_by_name(db, username=x_user or "default_owner")
    return crud.get_machines_for_user(db, owner_id=owner.id)

@router.post("/machines", response_model=schemas.MachineResponse)
def create_machine(
    machine: schemas.MachineCreate,
    x_user: str | None = Header(default=None),
    db: Session = Depends(database.get_db),
):
    db_machine = db.query(models.Machine).filter(models.Machine.name == machine.name).first()
    if db_machine:
        return db_machine
    owner = crud.get_or_create_user_by_name(db, username=x_user or "default_owner")
    return crud.create_machine(db, machine, owner_id=owner.id)

@router.delete("/machines/{machine_id}")
def delete_machine(machine_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_machine(db, machine_id=machine_id)
    if not success:
        raise HTTPException(status_code=404, detail="Machine not found")
    return {"message": "Machine deleted"}

@router.post("/predict", response_model=schemas.MachineLogResponse)
def predict_and_log(data: schemas.VibrationData, db: Session = Depends(database.get_db)):
    sensor_features = [data.sensor_1, data.sensor_2, data.sensor_3, data.sensor_4]
    try:
        rul_value = predict_rul(sensor_features, machine_id=data.machine_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

    status = "Normal" if rul_value > 50 else ("Warning" if rul_value > 20 else "Critical")

    log_create = schemas.MachineLogCreate(
        machine_id=data.machine_id,
        rul_prediction=rul_value,
        status=status,
        ai_log=f"Inference successful. Mode: {'Dataset' if data.is_dataset else 'Analysis'}",
        is_dataset=data.is_dataset
    )
    return crud.create_machine_log(db=db, log=log_create)

def normalize_sensor_columns(df):
    """Normalize sensor column names to s1-s4 or equivalents."""
    cols_lower = {str(c).lower(): c for c in df.columns}
    # If already has common names, return as is
    for p in ['s1', 's2', 's3', 's4', '0', '1', '2']:
        if p in cols_lower:
            return df
    # Otherwise, if it has at least 3 columns, assume first 3-4 are sensors
    if len(df.columns) >= 3:
        df = df.copy()
        df.columns = [str(c) for c in df.columns]
        num_cols = min(len(df.columns), 4)
        first_cols = list(df.columns)[:num_cols]
        rename = {first_cols[i]: f's{i+1}' for i in range(num_cols)}
        df = df.rename(columns=rename)
    return df

@router.post("/upload-logs")
async def upload_batch_logs(
    machine_id: str,
    file: UploadFile = File(...), 
    is_dataset: bool = False,
    db: Session = Depends(database.get_db)
):
    extension = file.filename.split('.')[-1].lower()
    if extension not in ['csv', 'h5', 'zip']:
        raise HTTPException(status_code=400, detail="Only CSV, H5 and ZIP files allowed")
    
    contents = await file.read()
    processed_count = 0

    async def process_dataframe(df, source_name):
        nonlocal processed_count
        
        print(f"DEBUG: Processing dataframe from {source_name}. Shape: {df.shape}")
        df = normalize_sensor_columns(df)
        cols = {str(c).lower(): c for c in df.columns}
        
        # Determine model type for strategy
        model = get_model(machine_id)
        is_advanced = isinstance(model, AdvancedCNCModel)
        
        s_maps = []
        num_sensors = 3 if is_advanced else 4
        
        for i in range(1, num_sensors + 1):
            found = False
            for p in [f's{i}', f'sensor_{i}', f'sensor{i}', f'vibration_{i}', str(i-1)]:
                if p in cols:
                    s_maps.append(cols[p])
                    found = True
                    break
            if not found:
                print(f"DEBUG Error: Sensor {i} not found in columns: {list(df.columns)}")
                return

        total_rows = len(df)
        batch_size = 1000
        
        if is_advanced:
            print(f"DEBUG: Using advanced windowed processing (1024 samples) for {total_rows} rows.")
            # Advanced model expects 1024x3 windows
            window_size = 1024
            # We can use sliding windows or non-overlapping blocks. 
            # Training used non-overlapping or at least distinct files.
            # Let's use non-overlapping blocks for efficiency.
            for start in range(0, total_rows, window_size):
                end = min(start + window_size, total_rows)
                window_df = df.iloc[start:end]
                
                # Extract the 3 sensors
                try:
                    window_data = window_df[s_maps].values.astype(np.float32)
                    
                    # predict_rul handles padding to 1024
                    rul = predict_rul(window_data, machine_id=machine_id)
                    status = "Normal" if rul > 50 else ("Warning" if rul > 20 else "Critical")
                    
                    db_log = models.MachineLog(
                        machine_id=machine_id,
                        rul_prediction=rul,
                        status=status,
                        ai_log=f"Advanced windowed log from {source_name} (rows {start}-{end})",
                        is_dataset=is_dataset
                    )
                    db.add(db_log)
                    processed_count += 1
                    
                    if (processed_count % 10) == 0:
                        db.commit()
                        print(f"DEBUG: Processed {end}/{total_rows} rows...")
                except Exception as e:
                    print(f"DEBUG Window Error at {start}: {e}")
                    continue
        else:
            print(f"DEBUG: Using standard row-by-row processing for {total_rows} rows.")
            for i, (_, row) in enumerate(df.iterrows()):
                try:
                    sensors = [float(row[c]) for c in s_maps]
                    while len(sensors) < 4: sensors.append(0.0)
                    
                    rul = predict_rul(sensors, machine_id=machine_id)
                    status = "Normal" if rul > 50 else ("Warning" if rul > 20 else "Critical")
                    
                    db_log = models.MachineLog(
                        machine_id=machine_id,
                        rul_prediction=rul,
                        status=status,
                        ai_log=f"Batch upload from {source_name}",
                        is_dataset=is_dataset
                    )
                    db.add(db_log)
                    processed_count += 1
                    
                    if (i + 1) % batch_size == 0:
                        db.commit()
                        print(f"DEBUG: Processed {i+1}/{total_rows} rows...")
                except Exception as e:
                    if i < 3: print(f"DEBUG Row Error at {i}: {e}")
                    continue
        
        db.commit()
        print(f"DEBUG: Finished {source_name}. Total so far: {processed_count}")

    try:
        if extension == 'csv':
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
            await process_dataframe(df, "CSV")
        elif extension == 'h5':
            with tempfile.NamedTemporaryFile(delete=False, suffix='.h5') as tmp:
                tmp.write(contents)
                tmp_path = tmp.name
            try:
                df = None
                error_log = []
                # Attempt 1: pandas auto read
                try:
                    df = pd.read_hdf(tmp_path)
                except Exception as e:
                    error_log.append(f"pd.read_hdf(auto) failed: {e}")
                
                # Attempt 2: key-based read (both pandas and h5py manual)
                if df is None:
                    try:
                        with h5py.File(tmp_path, 'r') as f:
                            keys = list(f.keys())
                            print(f"DEBUG: H5 Keys: {keys}")
                            for k in keys:
                                try:
                                    # Try pandas with key
                                    try:
                                        df = pd.read_hdf(tmp_path, key=k)
                                    except Exception:
                                        df = None
                                    
                                    # Fallback to manual numpy read
                                    if df is None:
                                        data = f[k][:]
                                        df = pd.DataFrame(data)
                                        # Auto-name columns if pure numeric
                                        if df.shape[1] >= 4 and all(isinstance(c, int) for c in df.columns):
                                            df.columns = [f's{i+1}' for i in range(df.shape[1])]
                                    
                                    if df is not None and not df.empty:
                                        print(f"DEBUG: Found data in key '{k}'")
                                        break
                                except Exception as e:
                                    error_log.append(f"Key {k} fail: {e}")
                    except Exception as e:
                        error_log.append(f"h5py open fail: {e}")
                
                if df is not None:
                    await process_dataframe(df, "H5")
                else:
                    raise HTTPException(status_code=400, detail=f"Could not read H5. Errors: {error_log}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        elif extension == 'zip':
            import zipfile
            with zipfile.ZipFile(io.BytesIO(contents)) as z:
                for zinfo in z.infolist():
                    if zinfo.filename.endswith(('.csv', '.h5')):
                        with z.open(zinfo) as f:
                            file_content = f.read()
                            if zinfo.filename.endswith('.csv'):
                                df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
                                await process_dataframe(df, zinfo.filename)
                            else: # .h5 in zip
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.h5') as tmp:
                                    tmp.write(file_content)
                                    tmp_path = tmp.name
                                    try:
                                        df = None
                                        try:
                                            df = pd.read_hdf(tmp_path)
                                        except Exception:
                                            # Try manual h5py fallback for zip-h5
                                            try:
                                                with h5py.File(tmp_path, 'r') as hf:
                                                    for k in hf.keys():
                                                        data = hf[k][:]
                                                        df = pd.DataFrame(data)
                                                        if df.shape[1] >= 4 and all(isinstance(c, int) for c in df.columns):
                                                            df.columns = [f's{i+1}' for i in range(df.shape[1])]
                                                        if not df.empty: break
                                            except Exception: pass
                                        
                                        if df is not None:
                                            await process_dataframe(df, zinfo.filename)
                                    finally:
                                        if os.path.exists(tmp_path): os.remove(tmp_path)

        return {"message": f"Successfully processed {processed_count} logs from {extension} archive/file"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/logs", response_model=list[schemas.MachineLogResponse])
def get_logs(machine_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_machine_logs(db, machine_id=machine_id, skip=skip, limit=limit)
