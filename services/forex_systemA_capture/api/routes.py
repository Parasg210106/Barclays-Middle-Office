from typing import List
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from services.forex_capture.models import Forex
from services.forex_capture.services.capture_service import forex_capture_service
import json
import os
from services.forex_capture.db.forex_repository import forex_repository
import csv
from services.firebase_client import get_firestore_client

REQUIRED_COLUMNS = [
    'Trade ID', 'Instrument', 'CurrencyPair', 'Quantity', 'Price', 'Buy/Sell', 'Settlement Date', 'Counterparty', 'Product Type'
]

router = APIRouter()

@router.post("/forex", response_model=Forex)
async def add_forex(forex: Forex):
    try:
        # Check for duplicate in Firestore
        if forex_repository.get_forex(forex.TradeID):
            raise HTTPException(status_code=400, detail=f"TradeID '{forex.TradeID}' already exists")
        forex_repository.save_forex(forex)
        return forex
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/forexs/bulk", response_model=List[Forex])
async def bulk_capture_forexs(forexs: List[Forex]):
    results = []
    errors = []
    for forex in forexs:
        try:
            if forex_repository.get_forex(forex.TradeID):
                raise Exception(f"TradeID '{forex.TradeID}' already exists")
            forex_repository.save_forex(forex)
            results.append(forex)
        except Exception as e:
            errors.append({"TradeID": forex.TradeID, "error": str(e)})
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    return results

@router.get("/forexs")
def get_forexs():

    return [f.dict() for f in forex_repository.load_forexs()]

@router.get("/forexs/{TradeID}", response_model=Forex)
async def get_forex(TradeID: str):
    forex = forex_capture_service.get_forex(TradeID)
    if forex:
        return forex
    raise HTTPException(status_code=404, detail="Forex not found")

@router.post("/upload_systemA_csv")
async def upload_systemA_csv(file: UploadFile = File(...)):
    db = get_firestore_client()
    content = await file.read()
    decoded = content.decode('utf-8').splitlines()
    reader = csv.DictReader(decoded)
    results = []
    for row in reader:
        # Normalize keys: strip spaces, lower-case, remove underscores
        norm_row = {k.strip().replace(' ', '').replace('_', '').lower(): v.strip() for k, v in row.items()}
        # Helper to get value by possible keys
        def get_val(*keys):
            for key in keys:
                k = key.strip().replace(' ', '').replace('_', '').lower()
                if k in norm_row:
                    return norm_row[k]
            return ''
        data = {
            'Trade ID': get_val('Trade ID', 'TradeID'),
            'Instrument': get_val('Instrument', 'CurrencyPair'),
            'FX Rate': get_val('FX Rate', 'FXRate', 'FxRate', 'Rate'),  # Keep original name
            'Notional Amount': get_val('Notional Amount', 'NotionalAmount', 'NotionalA'),  # Keep original name
            'Buy/Sell': get_val('Buy/Sell', 'BuySell'),
            'Settlement Date': get_val('Settlement Date', 'ValueDate', 'SettlementDate'),
            'Counterparty': get_val('Counterparty'),
            'Product Type': get_val('Product Type', 'ProductType'),
        }
        doc_id = data['Trade ID'] or None
        if doc_id:
            db.collection('fx_systemA_capture').document(doc_id).set(data)
        else:
            db.collection('fx_systemA_capture').add(data)
        results.append(data)
    return {"count": len(results), "stored": results}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}