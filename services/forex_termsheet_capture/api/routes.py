from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from services.forex_termsheet_capture.services.capture_service import forex_termsheet_capture_service
from services.forex_termsheet_capture.db.forex_repository import forex_repository

router = APIRouter()

@router.post("/forex-termsheets", response_model=List[Dict[str, Any]])
async def capture_termsheets(termsheets: List[Dict[str, Any]] = Body(...)):
    try:
        return forex_termsheet_capture_service.add_termsheets(termsheets)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/forex-termsheets", response_model=List[Dict[str, Any]])
async def list_termsheets():
    return [f.dict() for f in forex_repository.load_forexs()]

@router.get("/forex-termsheets/{tradeId}", response_model=Dict[str, Any])
async def get_termsheet_by_id(tradeId: str):
    termsheets = forex_repository.load_forexs()
    for t in termsheets:
        if t.get("TradeID") == tradeId:
            return t
    raise HTTPException(status_code=404, detail="Termsheet not found") 