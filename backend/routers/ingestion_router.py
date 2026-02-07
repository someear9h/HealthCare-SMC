from fastapi import APIRouter

# Deprecated single ingest router.
router = APIRouter()


@router.get("/deprecated")
async def deprecated():
    return {"status": "use /ingest/{hospital|lab|phc|ambulance}"}