import models, database
from sqlalchemy.orm import Session

db = next(database.get_db())
machines = db.query(models.Machine).all()
print(f"Machines: {[m.name for m in machines]}")

logs_count = db.query(models.MachineLog).count()
print(f"Logs count: {logs_count}")

api_keys = db.query(models.APIKey).all()
print(f"API Keys: {[(k.key, k.mode) for k in api_keys]}")
