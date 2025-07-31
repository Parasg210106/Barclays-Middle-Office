import json
import os

RULES_PATH = os.path.join(os.path.dirname(__file__), "equity_termsheet_rules.json")

def load_trade_rules():
    if not os.path.exists(RULES_PATH):
        # Create a default rules file if it doesn't exist
        default_rules = {
            "quantity": {"min": 1},
            "price": {"min": 0.01},
            "trade_type": {"allowed": ["BUY", "SELL"]},
            "unique_trade_id": True
        }
        with open(RULES_PATH, "w") as f:
            json.dump(default_rules, f, indent=2)
    with open(RULES_PATH, "r") as f:
        return json.load(f)

trade_rules = load_trade_rules()

trade_schema = {
    "TradeID": str,
    "OrderID": str,
    "ClientID": str,
    "ISIN": str,
    "Symbol": str,
    "TradeType": str,
    "Quantity": int,
    "Price": float,
    "TradeValue": float,
    "Currency": str,
    "TradeDate": str,
    "SettlementDate": str,
    "SettlementStatus": str,
    "Counterparty": str,
    "TradingVenue": str,
    "TraderName": str,
    "KYCStatus": str,
    "ReferenceDataValidated": str,
    "Commission": float,
    "Taxes": float,
    "TotalCost": float,
    "ConfirmationStatus": str,
    "CountryOfTrade": str,
    "OpsTeamNotes": str,
    "PricingSource": str,
    "MarketImpactCost": float,
    "FXRateApplied": float,
    "NetAmount": float,
    "CollateralRequired": float,
    "MarginType": str,
    "MarginStatus": str
} 