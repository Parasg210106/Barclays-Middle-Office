# Placeholder for trade repository DB access logic 

import json
from services.forex_capture.models import Forex
from typing import List, Optional
import os
from services.firebase_client import get_firestore_client
# Removed: from services.forex_termsheet_capture.db.termsheet_repository import save_termsheet

FOREX_FILE = os.path.join(os.path.dirname(__file__), 'forex.json')

class ForexRepository:
    def __init__(self, file_path=FOREX_FILE):
        self.file_path = file_path
        self.db = get_firestore_client()
        self.collection_name = "fx_capture"  # Use the premade collection for this service

    def save_forex(self, forex: Forex):
        print(f"[DEBUG] Saving forex trade to fx_capture: {forex.TradeID}")
        
        # Debug: Print the forex object data before saving
        forex_dict = forex.dict(by_alias=True)
        print(f"[DEBUG] Forex object data to save: {forex_dict}")
        
        # Debug: Check specific fields we're concerned about
        print(f"[DEBUG] Account_Number_Equity: '{forex_dict.get('Account_Number_Equity', 'NOT_FOUND')}'")
        print(f"[DEBUG] Account Number_Forex: '{forex_dict.get('Account Number_Forex', 'NOT_FOUND')}'")
        print(f"[DEBUG] ABA_Equity: '{forex_dict.get('ABA_Equity', 'NOT_FOUND')}'")
        print(f"[DEBUG] BSB_Equity: '{forex_dict.get('BSB_Equity', 'NOT_FOUND')}'")
        print(f"[DEBUG] Settlement_Method_Equity: '{forex_dict.get('Settlement_Method_Equity', 'NOT_FOUND')}'")
        
        self.db.collection(self.collection_name).document(forex.TradeID).set(forex_dict)
        # Removed: logic that creates and stores termsheet in fx_termsheets

    def load_forexs(self) -> List[Forex]:
        docs = self.db.collection(self.collection_name).stream()
        forexs = []
        for doc in docs:
            try:
                forexs.append(Forex.parse_obj(doc.to_dict()))
            except Exception as e:
                print(f"[DEBUG] Skipping invalid forex doc {doc.id}: {e}")
                print(f"[DEBUG] Document data: {doc.to_dict()}")
        return forexs

    def get_forex(self, TradeID: str) -> Optional[Forex]:
        print(f"[DEBUG] Checking for TradeID in Firestore: {TradeID}")
        doc = self.db.collection(self.collection_name).document(TradeID).get()
        print(f"[DEBUG] Firestore document exists: {doc.exists}")
        if doc.exists:
            print(f"[DEBUG] Firestore document data: {doc.to_dict()}")
            return Forex.parse_obj(doc.to_dict())
        return None

    def _load_forexs_raw(self) -> List[dict]:
        docs = self.db.collection(self.collection_name).stream()
        return [doc.to_dict() for doc in docs]

forex_repository = ForexRepository() 