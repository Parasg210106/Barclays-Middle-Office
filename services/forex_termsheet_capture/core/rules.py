import json
import os

RULES_PATH = os.path.join(os.path.dirname(__file__), "forex_rules.json")

def load_forex_rules():
    if not os.path.exists(RULES_PATH):
        # Create a default rules file if it doesn't exist
        default_rules = {
			"ProductType": {"allowed": ["FORWARD", "SWAP", "SPOT"]},
            "BuySell": {"allowed": ["BUY", "SELL"]},
            "unique_trade_id": True
        }
        with open(RULES_PATH, "w") as f:
            json.dump(default_rules, f, indent=2)
    with open(RULES_PATH, "r") as f:
        return json.load(f)

forex_rules = load_forex_rules()

forex_schema = {
    "TradeID": str,
    "TradeDate": str,
    "ValueDate": str,
    "TradeTime": str,
    "TraderID": str,
    "Counterparty": str,
    "CurrencyPair": str,
    "BuySell": str,
    "DealtCurrency": str,
    "BaseCurrency": str,
    "TermCurrency": str,
    "NotionalAmount": float,
    "FXRate": float,
    "TradeStatus": str,
    "SettlementStatus": str,
    "SettlementMethod": str,
    "Broker": str,
    "ExecutionVenue": str,
    "ProductType": str,
    "MaturityDate": str,
    "ConfirmationTimestamp": str,
    "SettlementDate": str,
    "BookingLocation": str,
    "Portfolio": str,
    "TradeVersion": int,
    "CancellationFlag": str,
    "AmendmentFlag": str,
    "RiskSystemID": str,
    "RegulatoryReportingStatus": str,
    "TradeSourceSystem": str,
    "ConfirmationMethod": str,
    "ConfirmationStatus": str,
    "SettlementInstructions": str,
    "Custodian": str,
    "NettingEligibility": str,
    "TradeComplianceStatus": str,
    "KYCCheck": str,
    "SanctionsScreening": str,
    "ExceptionFlag": str,
    "ExceptionNotes": str,
    "AuditTrailRef": str,
    "CommissionAmount": float,
    "CommissionCurrency": str,
    "BrokerageFee": float,
    "BrokerageCurrency": str,
    "CustodyFee": float,
    "CustodyCurrency": str,
    "SettlementCost": float,
    "SettlementCurrency": str,
    "FXGainLoss": float,
    "PnlCalculated": float,
    "CostAllocationStatus": str,
    "CostCenter": str,
    "ExpenseApprovalStatus": str,
    "CostBookedDate": str
} 