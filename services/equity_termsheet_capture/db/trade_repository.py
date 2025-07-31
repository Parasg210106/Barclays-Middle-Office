# Placeholder for trade repository DB access logic 

import json
from shared.models import Trade
from typing import List, Optional
import os
from services.firebase_client import get_firestore_client

TRADES_FILE = os.path.join(os.path.dirname(__file__), 'trades.json')

class TradeRepository:
    def __init__(self, file_path=TRADES_FILE):
        self.file_path = file_path
        self.db = get_firestore_client()

    def save_trade(self, trade: Trade):
        self.db.collection("equity_termsheet_trades").document(trade.trade_id).set(trade.dict(by_alias=True))

    def load_trades(self) -> List[Trade]:
        docs = self.db.collection("equity_termsheet_trades").stream()
        return [Trade.parse_obj(doc.to_dict()) for doc in docs]

    def get_trade(self, trade_id: str) -> Optional[Trade]:
        doc = self.db.collection("equity_termsheet_trades").document(trade_id).get()
        if doc.exists:
            return Trade.parse_obj(doc.to_dict())
        return None

    def _load_trades_raw(self) -> List[dict]:
        docs = self.db.collection("equity_termsheet_trades").stream()
        return [doc.to_dict() for doc in docs]

trade_repository = TradeRepository() 