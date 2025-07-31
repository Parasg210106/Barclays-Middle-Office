from pydantic import BaseModel
from typing import Optional

class Equity(BaseModel):
    TradeID: str
    TradeType: str
    Quantity: int
    Symbol: str
    Price: float
    TradeValue: float
    SettlementDate: str
    Source: str = "BackOffice"  # Default source for BO entry