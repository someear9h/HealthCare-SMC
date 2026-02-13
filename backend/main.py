from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Ensure this matches your filename (e.g., ingestion_router.py or patient_router.py)
from routers.ingestion_router import router as patient_ingestion_router 
from routers.risk_router import router as risk_router
from routers.logs_router import router as logs_router
from routers.facility_status_router import router as facility_status_router
from routers.analytics_router import router as analytics_router
from routers.ambulance_router import router as ambulance_router
from routers.admin_services import router as admin_services_router
from core.database import init_db

app = FastAPI(title="SMC Smart Health Intelligence API")

# Initialize database (creates 'patient_transactions' table)
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Required for local React dev on port 3001
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ########################################################################
# HUGE CHANGE: CLEANED UP ROUTER MAPPING
# Removed redundant inclusions to prevent Swagger UI confusion.
# ########################################################################
app.include_router(patient_ingestion_router, prefix="/ingest/patient", tags=["Ingest: Clinical Events"])
app.include_router(admin_services_router, prefix="/services", tags=["Admin: Citizen Engagement"])
app.include_router(logs_router) # Prefix /logs is inside the router
app.include_router(risk_router, prefix="/risk", tags=["Risk Engine"])
app.include_router(facility_status_router, prefix="/facility-status", tags=["Facility Status"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(ambulance_router, prefix="/ambulances", tags=["Ambulances"])

@app.get("/")
def root():
    return {
        "status": "online",
        "city": "Solapur",
        "system": "Unified Digital Health Ecosystem (UDHE)"
    }

if __name__ == "__main__":
    import uvicorn
    # Use standard uvicorn to support the WebSocket protocol in logs_router
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)