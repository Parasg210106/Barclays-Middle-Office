from typing import List
from fastapi import APIRouter, HTTPException
from shared.models import Trade
from services.equity_capture.services.capture_service import trade_capture_service
import json
import os
from services.equity_capture.db.trade_repository import trade_repository

router = APIRouter()

@router.post("/trades", response_model=Trade)
async def capture_trade(trade: Trade):
    try:
        return trade_capture_service.add_trade(trade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trades/bulk", response_model=List[Trade])
async def bulk_capture_trades(trades: List[Trade]):
    results = []
    errors = []
    for trade in trades:
        try:
            results.append(trade_capture_service.add_trade(trade))
        except ValueError as e:
            errors.append({"trade_id": trade.trade_id, "error": str(e)})
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    return results

@router.get("/trades")
def get_trades():
    return [t.dict() for t in trade_repository.load_trades()]

@router.get("/trades/{trade_id}", response_model=Trade)
async def get_trade(trade_id: str):
    trade = trade_capture_service.get_trade(trade_id)
    if trade:
        return trade
    raise HTTPException(status_code=404, detail="Trade not found")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"} 