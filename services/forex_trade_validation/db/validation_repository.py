import json
import os
from typing import List, Dict
from services.firebase_client import get_firestore_client

class ValidationRepository:
    def __init__(self, db_path: str = "validated_trades.json"):
        self.db_path = db_path
        self.db = get_firestore_client()

    def _ensure_db_exists(self):
        """Ensure the database file exists with an empty list if it doesn't."""
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump([], f)

    def save_validation_results(self, results: List[Dict]) -> bool:
        """Save validation results to the database."""
        try:
            for result in results:
                trade_id = result.get("TradeID") or result.get("trade_id")
                if trade_id:
                    self.db.collection("forex_validation_results").document(str(trade_id)).set(result)
            return True
        except Exception:
            try:
                with open(self.db_path, 'w') as f:
                    json.dump(results, f, indent=2)
                return True
            except Exception as e:
    
                return False

    def get_all_validated_trades(self) -> List[Dict]:
        """Retrieve all validated trades from the database."""
        try:
            docs = self.db.collection("forex_validation_results").stream()
            return [doc.to_dict() for doc in docs]
        except Exception:
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
    
                return []

    def get_trade_by_id(self, trade_id: str) -> Dict:
        """Retrieve a specific trade by its ID."""
        try:
            doc = self.db.collection("forex_validation_results").document(trade_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            trades = self.get_all_validated_trades()
            for trade in trades:
                if trade.get("TradeID") == trade_id:
                    return trade
        return None

    def get_failed_trades(self) -> List[Dict]:
        """Retrieve all trades that failed validation."""
        trades = self.get_all_validated_trades()
        return [trade for trade in trades if not trade.get("is_valid", True)]

    def get_passed_trades(self) -> List[Dict]:
        """Retrieve all trades that passed validation."""
        trades = self.get_all_validated_trades()
        return [trade for trade in trades if trade.get("is_valid", False)]

    def clear_database(self) -> bool:
        """Clear all data from the database."""
        try:
            docs = self.db.collection("forex_validation_results").stream()
            for doc in docs:
                self.db.collection("forex_validation_results").document(doc.id).delete()
            return True
        except Exception:
            try:
                with open(self.db_path, 'w') as f:
                    json.dump([], f)
                return True
            except Exception as e:
    
                return False
