import models, database, crud, schemas
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

def seed():
    db = next(database.get_db())
    
    # 1. Ensure user exists (owner_id=1)
    user = db.query(models.User).filter(models.User.id == 1).first()
    if not user:
        user = models.User(id=1, username="admin", hashed_password="fake")
        db.add(user)
        db.commit()
    
    # 2. Add preset machines
    machine_names = ["M01", "M02", "M03"]
    machines = []
    for name in machine_names:
        m = db.query(models.Machine).filter(models.Machine.name == name).first()
        if not m:
            print(f"Creating machine: {name}")
            m = crud.create_machine(db, schemas.MachineCreate(name=name), owner_id=1)
        machines.append(m)
    
    # 3. Add API Keys for each machine
    for m in machines:
        # Check if key already exists
        prefix = m.name.lower()
        key_exists = db.query(models.APIKey).filter(models.APIKey.machine_id == m.id).first()
        if not key_exists:
            print(f"Creating keys for {m.name}")
            db.add(models.APIKey(key=f"key_{prefix}_analysis", owner_id=1, mode="analysis", machine_id=m.id))
            db.add(models.APIKey(key=f"key_{prefix}_dataset", owner_id=1, mode="dataset", machine_id=m.id))
    db.commit()

    # 4. Add some logs for each machine
    for m in machines:
        name = m.name
        log_count = db.query(models.MachineLog).filter(models.MachineLog.machine_id == name).count()
        if log_count < 5:
            print(f"Adding logs for {name}...")
            for i in range(10):
                rul = random.uniform(10, 90)
                status = "Normal" if rul > 50 else ("Warning" if rul > 20 else "Critical")
                crud.create_machine_log(db, schemas.MachineLogCreate(
                    machine_id=name,
                    rul_prediction=rul,
                    status=status,
                    ai_log=f"Seed log {i+1} for {name}",
                    is_dataset=False
                ))
    
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
