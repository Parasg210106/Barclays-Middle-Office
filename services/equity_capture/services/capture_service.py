from shared.models import Trade
from typing import List, Optional
from services.equity_capture.db.trade_repository import trade_repository
from services.equity_capture.core.rules import trade_rules

class TradeCaptureService:
    def add_trade(self, trade: Trade) -> Trade:
        # Rule: Quantity min
        if trade.quantity < trade_rules["quantity"]["min"]:
            raise ValueError(f"Quantity must be at least {trade_rules['quantity']['min']}")
        # Rule: Price min
        if trade.price < trade_rules["price"]["min"]:
            raise ValueError(f"Price must be at least {trade_rules['price']['min']}")
        # Rule: Allowed trade types
        if trade.trade_type not in trade_rules["trade_type"]["allowed"]:
            raise ValueError(f"TradeType must be one of {trade_rules['trade_type']['allowed']}")
        # Rule: Unique TradeID
        if trade_rules.get("unique_trade_id") and self.get_trade(trade.trade_id):
            raise ValueError(f"TradeID '{trade.trade_id}' already exists")
        trade_repository.save_trade(trade)
        return trade

    def list_trades(self) -> List[Trade]:
        return trade_repository.load_trades()

    def get_trade(self, trade_id: str) -> Optional[Trade]:
        return trade_repository.get_trade(trade_id)

# Singleton instance
trade_capture_service = TradeCaptureService() 