import logging
import sys
from datetime import datetime, timezone

# Basic logging to stdout for cloud visibility
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("--- BACKEND STARTING UP ---")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, SessionLocal
from routes import router
import crud

app = FastAPI(title="AI Predictive Maintenance Platform - API")

# Move DB initialization to startup event to avoid blocking imports
@app.on_event("startup")
def startup_event():
    try:
        models.Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            owner = crud.get_or_create_default_owner(db)
            crud.ensure_default_machines(db, owner_id=owner.id)
    except Exception as e:
        print(f"Startup error: {e}")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Predictive Maintenance API"}

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
