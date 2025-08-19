# Placeholder for trade repository DB access logic 

import json
from services.forex_capture.models import Forex
from typing import List, Optional
import os
from services.firebase_client import get_firestore_client
from services.forex_capture.services.unified_data_service import unified_data_service
# Removed: from services.forex_termsheet_capture.db.termsheet_repository import save_termsheet

FOREX_FILE = os.path.join(os.path.dirname(__file__), '../db/forex.json')

class ForexRepository:
    def __init__(self, file_path=FOREX_FILE):
        self.file_path = file_path
        self.db = get_firestore_client()
        self.collection_name = "fx_capture"  # Use the premade collection for this service

    def save_forex(self, forex: Forex, client_id: str = None):
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
        
        # Save to fx_capture collection (existing functionality)
        self.db.collection(self.collection_name).document(forex.TradeID).set(forex_dict)
        
        # Note: unified_data updates are handled by the calling API route
        # to prevent duplicate execution
        print(f"[DEBUG] Successfully saved trade {forex.TradeID} to fx_capture. Unified data updates handled by API route.")
        
        # Removed: logic that creates and stores termsheet in fx_termsheets

    def save_forex_bulk(self, forexs: List[Forex], client_id: str = None):
        """
        Save multiple forex trades to fx_capture collection.
        Note: unified_data updates are handled by the calling API route to avoid duplication.
        
        Args:
            forexs: List of Forex trade objects to save
            client_id: The client ID (kept for compatibility but not used here)
        """
        print(f"[DEBUG] Saving {len(forexs)} forex trades to fx_capture")
        
        # Save each trade to fx_capture collection (existing functionality)
        for i, forex in enumerate(forexs):
            print(f"[DEBUG] Saving trade {i+1}/{len(forexs)}: {forex.TradeID}")
            forex_dict = forex.dict(by_alias=True)
            self.db.collection(self.collection_name).document(forex.TradeID).set(forex_dict)
        
        # Note: unified_data updates are handled by the calling API route
        # to prevent duplicate execution of the bulk update logic
        print(f"[DEBUG] Saved {len(forexs)} trades to fx_capture. Unified data updates handled by API route.")

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