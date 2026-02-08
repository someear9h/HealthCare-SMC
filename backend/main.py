from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.ingestion_router import router as ingestion_router
from routers.risk_router import router as risk_router
from routers.outbreak_router import router as outbreak_router
from routers.ingest_hospital import router as hospital_router
from routers.ingest_lab import router as lab_router
from routers.ingest_phc import router as phc_router
from routers.ingest_ambulance import router as ingest_ambulance_router
from routers.logs_router import router as logs_router
from routers.facility_status_router import router as facility_status_router
from routers.analytics_router import router as analytics_router
from routers.ambulance_router import router as ambulance_router
from core.database import init_db

app = FastAPI(title="Health Intelligence API")

# Initialize database (create tables on startup)
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk_router, prefix="/risk", tags=["Risk Engine"])
app.include_router(outbreak_router, prefix="/outbreaks", tags=["Outbreak Detection"])
app.include_router(ingestion_router, prefix="/ingestion", tags=["Data Ingestion"])
app.include_router(hospital_router, tags=["Ingest: Hospital"])
app.include_router(lab_router, tags=["Ingest: Lab"])
app.include_router(phc_router, tags=["Ingest: PHC"])
app.include_router(ingest_ambulance_router, tags=["Ingest: Ambulance"])
app.include_router(logs_router, tags=["Logs"])
app.include_router(facility_status_router, prefix="/facility-status", tags=["Facility Status"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(ambulance_router, prefix="/ambulances", tags=["Ambulances"])

@app.get("/")
def root():
    return {"message": "Health Intelligence Running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)