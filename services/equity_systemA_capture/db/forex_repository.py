# Placeholder for trade repository DB access logic 

import json
from services.forex_capture.models import Forex
from typing import List, Optional
import os
from services.firebase_client import get_firestore_client
from services.forex_termsheet_capture.db.termsheet_repository import save_termsheet

FOREX_FILE = os.path.join(os.path.dirname(__file__), 'forex.json')

class ForexRepository:
    def __init__(self, file_path=FOREX_FILE):
        self.file_path = file_path
        self.db = get_firestore_client()
        self.collection_name = "fx_capture"  # Use the premade collection for this service

    def save_forex(self, forex: Forex):
        print(f"[DEBUG] Saving forex trade to fx_capture: {forex.TradeID}")
        self.db.collection(self.collection_name).document(forex.TradeID).set(forex.dict(by_alias=True))
        # Create and store termsheet in fx_termsheets
        termsheet = {
            'TermsheetID': forex.TradeID,
            'TradeID': forex.TradeID,
            'TradeDate': forex.TradeDate,
            'Counterparty': forex.Counterparty,
            'CurrencyPair': forex.CurrencyPair,
            'BuySell': forex.BuySell,
            'DealtCurrency': forex.DealtCurrency,
            'BaseCurrency': forex.BaseCurrency,
            'TermCurrency': forex.TermCurrency,
            'NotionalAmount': forex.NotionalAmount,
            'FXRate': forex.FXRate,
            'ProductType': forex.ProductType,
            'MaturityDate': forex.MaturityDate,
            'SettlementDate': forex.SettlementDate,
            'KYCCheck': forex.KYCCheck,
            # Add more fields as needed
        }
        save_termsheet(termsheet)

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