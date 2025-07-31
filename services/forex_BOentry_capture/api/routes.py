from fastapi import APIRouter, File, UploadFile
import csv
from services.firebase_client import get_firestore_client

router = APIRouter()

@router.post("/upload_BOentry_csv")
async def upload_BOentry_csv(file: UploadFile = File(...)):
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
            db.collection('fx_BOentry_capture').document(doc_id).set(data)
        else:
            db.collection('fx_BOentry_capture').add(data)
        results.append(data)
    return {"count": len(results), "stored": results}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}