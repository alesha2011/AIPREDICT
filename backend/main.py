from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, SessionLocal
from routes import router
import crud

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# Seed default machines M01-M03
with SessionLocal() as db:
    owner = crud.get_or_create_default_owner(db)
    crud.ensure_default_machines(db, owner_id=owner.id)

app = FastAPI(title="AI Predictive Maintenance Platform - API")

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
