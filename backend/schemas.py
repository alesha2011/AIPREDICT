from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class VibrationData(BaseModel):
    machine_id: str
    sensor_1: float
    sensor_2: float
    sensor_3: float
    sensor_4: float
    is_dataset: Optional[bool] = False

class APIKeyCreate(BaseModel):
    mode: str # "dataset" or "analysis"
    machine_id: Optional[int] = None

class APIKeyUpdate(BaseModel):
    mode: str

class APIKeyResponse(BaseModel):
    id: int
    key: str
    mode: str
    machine_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    username: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class MachineCreate(BaseModel):
    name: str

class MachineResponse(BaseModel):
    id: int
    name: str
    owner_id: Optional[int] = None  # NULL для общих станков M01, M02, M03
    created_at: datetime

    class Config:
        from_attributes = True

class MachineLogBase(BaseModel):
    machine_id: str
    rul_prediction: float
    status: str
    ai_log: str
    is_dataset: bool

class MachineLogCreate(MachineLogBase):
    pass

class MachineLogResponse(MachineLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
