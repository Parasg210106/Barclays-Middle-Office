from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from services.equity_termsheet_capture.services.capture_service import equity_termsheet_capture_service

router = APIRouter()

@router.post("/equity-termsheets", response_model=List[Dict[str, Any]])
async def capture_termsheets(termsheets: List[Dict[str, Any]] = Body(...)):
    """Add multiple termsheets to Firebase"""
    try:
        return equity_termsheet_capture_service.add_termsheets(termsheets)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/equity-termsheets/single", response_model=Dict[str, Any])
async def capture_single_termsheet(termsheet: Dict[str, Any] = Body(...)):
    """Add a single termsheet to Firebase"""
    try:
        return equity_termsheet_capture_service.add_single_termsheet(termsheet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/equity-termsheets", response_model=List[Dict[str, Any]])
async def list_termsheets():
    """List all termsheets from Firebase"""
    return equity_termsheet_capture_service.list_termsheets()

@router.get("/equity-termsheets/{tradeId}", response_model=Dict[str, Any])
async def get_termsheet_by_id(tradeId: str):
    """Get a specific termsheet by Trade ID from Firebase"""
    termsheet = equity_termsheet_capture_service.get_termsheet_by_trade_id(tradeId)
    if termsheet is None:
        raise HTTPException(status_code=404, detail="Termsheet not found")
    return termsheet 