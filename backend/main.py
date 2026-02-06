from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.risk_router import router as risk_router

app = FastAPI(title="Health Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk_router, prefix="/risk", tags=["Risk Engine"])


@app.get("/")
def root():
    return {"message": "Health Intelligence Running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)