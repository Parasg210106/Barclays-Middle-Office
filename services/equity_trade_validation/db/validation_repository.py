import json
import os
from services.firebase_client import get_firestore_client

TRADES_FILE = "db/trades.json"
VALIDATED_FILE = "db/validated_trades.json"

def load_trades():
    if not os.path.exists(TRADES_FILE):
        return []
    with open(TRADES_FILE, "r") as f:
        return json.load(f)

def save_validated_trades(results):
    with open(VALIDATED_FILE, "w") as f:
        json.dump(results, f, indent=2)
    # Sync to Firestore
    db = get_firestore_client()
    for result in results:
        trade_id = result.get("Trade ID") or result.get("trade_id")
        if trade_id:
            db.collection("validation_results").document(str(trade_id)).set(result)

def load_validated_trades():
    if not os.path.exists(VALIDATED_FILE):
        return []
    with open(VALIDATED_FILE, "r") as f:
        return json.load(f)
