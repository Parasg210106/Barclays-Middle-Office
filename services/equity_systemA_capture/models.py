from pydantic import BaseModel
from typing import Optional

class Equity(BaseModel):
    TradeID: str
    TradeType: str
    Quantity: int
    Symbol: str
    Price: float
    TradeValue: float
    Source: str = "SystemA"  # Default source for System A