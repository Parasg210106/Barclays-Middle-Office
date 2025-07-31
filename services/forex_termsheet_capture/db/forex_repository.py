# Placeholder for trade repository DB access logic 

import json
from services.forex_capture.models import Forex
from typing import List, Optional
import os
from services.firebase_client import get_firestore_client

FOREXS_FILE = os.path.join(os.path.dirname(__file__), 'forexs.json')

class ForexRepository:
    def __init__(self, file_path=FOREXS_FILE):
        self.file_path = file_path
        self.db = get_firestore_client()

    def save_forex(self, forex: Forex):
        self.db.collection("forex_termsheet").document(forex.TradeID).set(forex.dict(by_alias=True))

    def load_forexs(self) -> List[Forex]:
        docs = self.db.collection("forex_termsheet").stream()
        return [Forex.parse_obj(doc.to_dict()) for doc in docs]

    def get_forex(self, TradeID: str) -> Optional[Forex]:
        doc = self.db.collection("forex_termsheet").document(TradeID).get()
        if doc.exists:
            return Forex.parse_obj(doc.to_dict())
        return None

    def _load_forexs_raw(self) -> List[dict]:
        docs = self.db.collection("forex_termsheet").stream()
        return [doc.to_dict() for doc in docs]

forex_repository = ForexRepository() 