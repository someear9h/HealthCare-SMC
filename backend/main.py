from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.ingestion_router import router as ingestion_router
from routers.risk_router import router as risk_router
from routers.outbreak_router import router as outbreak_router

app = FastAPI(title="Health Intelligence API")

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

@app.get("/")
def root():
    return {"message": "Health Intelligence Running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)