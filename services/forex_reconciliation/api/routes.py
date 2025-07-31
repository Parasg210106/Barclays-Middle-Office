from fastapi import APIRouter, UploadFile, File
from services.forex_reconciliation.services.reconciliation_service import reconcile_trades
from services.forex_reconciliation.shared.trade_sources import capture_trade_data
import json

router = APIRouter()

@router.get("/test")
def test():

    return {"message": "test ok"}

@router.post("/upload/bulk")
async def upload_bulk_trades(file: UploadFile = File(...)):
    contents = await file.read()
    trades = json.loads(contents)
    capture_trade_data(trades)
    return {"message": "Trades uploaded successfully", "count": len(trades)}

@router.get("/reconcile/{system_type}")
def reconcile(system_type: str, save_to_firebase: bool = True):  # system_type: "FO-FO" or "FO-BO"
    result = reconcile_trades(system_type, save_to_firebase=save_to_firebase)
    return {"reconciliation_result": result}
