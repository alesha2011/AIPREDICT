from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
import models, schemas
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_or_create_default_owner(db: Session) -> models.User:
    """
    Ensures there is at least one user in the system that can be used
    as the owner for machines and API keys when no real auth is wired.
    """
    user = db.query(models.User).filter(models.User.username == "default_owner").first()
    if user:
        return user

    hashed_password = pwd_context.hash("default_password")
    user = models.User(username="default_owner", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_or_create_user_by_name(db: Session, username: str) -> models.User:
    user = get_user_by_username(db, username=username)
    if user:
        return user
    hashed_password = pwd_context.hash("default_password")
    user = models.User(username=username, hashed_password=hashed_password)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        user = get_user_by_username(db, username=username)
        if user:
            return user
        raise

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# API Keys
def create_api_key(db: Session, owner_id: int, mode: str, machine_id: int = None):
    new_key = secrets.token_urlsafe(32)
    db_key = models.APIKey(key=new_key, owner_id=owner_id, mode=mode, machine_id=machine_id)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key

def get_api_keys(db: Session, owner_id: int, machine_id: int = None):
    query = db.query(models.APIKey).filter(models.APIKey.owner_id == owner_id)
    if machine_id:
        query = query.filter(models.APIKey.machine_id == machine_id)
    return query.all()

def update_api_key(db: Session, key_id: int, mode: str):
    db_key = db.query(models.APIKey).filter(models.APIKey.id == key_id).first()
    if db_key:
        db_key.mode = mode
        db.commit()
        db.refresh(db_key)
    return db_key

def validate_api_key(db: Session, key: str):
    return db.query(models.APIKey).filter(models.APIKey.key == key).first()

# Machines
def create_machine(db: Session, machine: schemas.MachineCreate, owner_id: int):
    db_machine = models.Machine(name=machine.name, owner_id=owner_id)
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

def get_machines(db: Session, owner_id: int):
    return db.query(models.Machine).filter(models.Machine.owner_id == owner_id).all()

def get_machines_for_user(db: Session, owner_id: int):
    """
    Return shared machines (owner_id is NULL) + machines belonging to this user.
    """
    from sqlalchemy import or_
    return (
        db.query(models.Machine)
        .filter(
            or_(
                models.Machine.owner_id.is_(None),  # shared M01, M02, M03
                models.Machine.owner_id == owner_id,
            )
        )
        .order_by(models.Machine.name)
        .all()
    )

def ensure_default_machines(db: Session, owner_id: int):
    """
    Create default shared machines M01, M02, M03 if they don't exist yet.
    Shared = owner_id is NULL so that all users see them.
    """
    default_names = ["M01", "M02", "M03"]
    existing = db.query(models.Machine).filter(models.Machine.name.in_(default_names)).all()
    existing_names = {m.name for m in existing}

    for name in default_names:
        if name not in existing_names:
            db_machine = models.Machine(name=name, owner_id=None)
            db.add(db_machine)

    if len(existing_names) < len(default_names):
        db.commit()

def create_machine_log(db: Session, log: schemas.MachineLogCreate):
    db_log = models.MachineLog(
        machine_id=log.machine_id,
        rul_prediction=log.rul_prediction,
        status=log.status,
        ai_log=log.ai_log,
        is_dataset=log.is_dataset
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def delete_machine(db: Session, machine_id: int):
    db_machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if db_machine:
        # Do not allow delete of shared machines
        if db_machine.owner_id is None:
            return None
        # Also delete all logs for this machine
        db.query(models.MachineLog).filter(models.MachineLog.machine_id == db_machine.name).delete()
        db.delete(db_machine)
        db.commit()
    return db_machine

def get_machine_logs(db: Session, machine_id: str = None, skip: int = 0, limit: int = 100):
    query = db.query(models.MachineLog).order_by(models.MachineLog.timestamp.desc())
    if machine_id:
        query = query.filter(models.MachineLog.machine_id == machine_id)
    return query.offset(skip).limit(limit).all()
