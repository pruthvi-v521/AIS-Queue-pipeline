from fastapi import FastAPI
from app.routers import vessels
from .routers import health, vessels, positions , monitoring

app = FastAPI(title="AIS Streaming API")

app.include_router(health.router)
app.include_router(vessels.router)
app.include_router(positions.router)
app.include_router(monitoring.router)

@app.get("/")
def root():
    return {"message": "AIS API Framework"}

