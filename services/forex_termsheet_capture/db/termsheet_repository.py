import json
import os
from services.firebase_client import get_firestore_client

TERMSHEETS_FILE = os.path.join(os.path.dirname(__file__), 'termsheets.json')

def save_termsheet(termsheet):
    db = get_firestore_client()
    # Accept common variations for the unique identifier
    possible_keys = [
        'TermsheetID', 'Termsheet Id', 'termsheetid', 'termsheet_id',
        'TradeID', 'Trade Id', 'tradeid', 'trade_id',
        'id', 'ID'
    ]
    termsheet_id = None
    for key in possible_keys:
        if key in termsheet and termsheet[key]:
            termsheet_id = termsheet[key]
            break
    if not termsheet_id:
        raise ValueError("Termsheet must have a unique identifier field (e.g., 'TermsheetID', 'TradeID', 'id', or common variations thereof). Found keys: " + str(list(termsheet.keys())))
    db.collection('fx_termsheet').document(str(termsheet_id)).set(termsheet)

def load_termsheets():
    db = get_firestore_client()
    docs = db.collection('fx_termsheet').stream()
    return [doc.to_dict() for doc in docs] 