import json
from services.equity_trade_validation.core import validators
import requests

TERMSHEET_SERVICE_URL = "http://localhost:8010"

class RulesEngine:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.rules_config = json.load(f)

    def fetch_termsheet(self, trade_id):
        try:
            resp = requests.get(f"{TERMSHEET_SERVICE_URL}/termsheets/{trade_id}", timeout=3)
            if resp.status_code == 200:
                return resp.json().get("termsheet")
            else:
                return None
        except Exception as e:
            return None

    def validate_trade(self, trade: dict) -> dict:
        errors = []

        # Run all validation checks in order
        errors.extend(validators.check_mandatory_fields(trade, self.rules_config["mandatory_fields"]))
        errors.extend(validators.check_format_rules(trade, self.rules_config["format_rules"]))
        errors.extend(validators.check_logical_rules(trade))
        errors.extend(validators.check_static_values(trade, self.rules_config["static_validation"]))
        errors.extend(validators.check_custom_rules(trade, self.rules_config["custom_rules"]))

        # --- Termsheet comparison integration ---
        trade_id = trade.get("Trade ID") or trade.get("trade_id")
        if trade_id:
            termsheet = self.fetch_termsheet(trade_id)
            if not termsheet:
                errors.append("Termsheet not found or service unavailable for trade_id: {}".format(trade_id))
            else:
                # Compare all mandatory fields from rules_config.json
                mandatory_fields = self.rules_config["mandatory_fields"]
                for field in mandatory_fields:
                    trade_value = trade.get(field)
                    termsheet_value = termsheet.get(field)
                    if str(trade_value) != str(termsheet_value):
                        errors.append(f"{field} mismatch: trade='{trade_value}' vs termsheet='{termsheet_value}'")
        else:
            errors.append("Trade ID missing, cannot fetch termsheet.")

        return {
            "Trade ID": trade.get("Trade ID", "UNKNOWN"),
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def validate_trades(self, trade_list: list) -> list:
        results = []
        for trade in trade_list:
            result = self.validate_trade(trade)
            results.append(result)
        return results
