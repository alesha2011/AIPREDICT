from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
from database import Base
import secrets

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)
    mode = Column(String)  # "dataset" or "analysis"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class MachineLog(Base):
    __tablename__ = "machine_logs"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, index=True) # References Machine.name
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    rul_prediction = Column(Float)
    status = Column(String)
    ai_log = Column(String)
    is_dataset = Column(Boolean, default=False)
