import json
import os
from services.forex_capture.models import Forex
from services.forex_capture.db.forex_repository import forex_repository
from typing import List, Optional

FOREX_JSON_PATH = os.path.join(os.path.dirname(__file__), '../db/forex.json')
FOREX_JSON_PATH = os.path.abspath(FOREX_JSON_PATH)

class ForexCaptureService:
    def list_forexs(self) -> List[Forex]:
        return forex_repository.load_forexs()

    def get_forex(self, TradeID: str) -> Optional[Forex]:
        return forex_repository.get_forex(TradeID)

forex_capture_service = ForexCaptureService() 