import json
import os
from services.firebase_client import get_firestore_client

CAPTURE_FILE_PATH = os.path.join(os.path.dirname(__file__), "capture.json")

def load_trades():
    db = get_firestore_client()
    trades = []
    
    # Get all documents from all equity capture collections
    collections = ['eq_systemA_capture', 'eq_systemB_capture', 'eq_FOentry_capture', 'eq_BOentry_capture']
    
    for collection_name in collections:
        docs = db.collection(collection_name).stream()
        for doc in docs:
            trade_data = doc.to_dict()
            trades.append(trade_data)
    
    return trades

def save_trades(trades):
    # This function is kept for compatibility but trades are now saved directly to Firebase
    # by the capture services
    pass
