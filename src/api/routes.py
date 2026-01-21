from fastapi import APIRouter, Query
from src.agentic_context import run_pipeline  # we’ll create this wrapper

router = APIRouter()

from fastapi import HTTPException

@router.get("/analyze")
def analyze_stock(ticker: str):
    try:
        return run_pipeline(ticker.upper())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

