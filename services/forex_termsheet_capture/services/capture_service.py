from services.forex_termsheet_capture.db.termsheet_repository import load_termsheets, save_termsheet
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.rules import forex_schema

# Only keep these columns for validation (including TradeID)
ALLOWED_COLUMNS = [
    "TradeID",
    "TradeDate",
    "Counterparty",
    "CurrencyPair",
    "BuySell",
    "DealtCurrency",
    "BaseCurrency",
    "TermCurrency",
    "NotionalAmount",
    "FXRate",
    "ProductType",
    "MaturityDate",
    "SettlementDate",
    "KYCCheck"
]

class ForexTermsheetCaptureService:
    def add_termsheets(self, termsheets):
        existing = load_termsheets()
        filtered_termsheets = [
            {k: t[k] for k in ALLOWED_COLUMNS if k in t}
            for t in termsheets
        ]
        existing.extend(filtered_termsheets)
        for t in filtered_termsheets: save_termsheet(t)
        return filtered_termsheets

    def list_termsheets(self):
        return load_termsheets()

forex_termsheet_capture_service = ForexTermsheetCaptureService() 