import logging
from services.forex_reconciliation.db.trade_repository import load_trades_fofo, load_trades_fobo
from services.forex_reconciliation.core import rules
from services.firebase_client import get_firestore_client

# Helper to normalize keys (strip spaces, convert to lowercase)
def normalize_dict_keys(d):
    normalized = {}
    for k, v in d.items():
        key = k.replace(' ', '').replace('_', '').lower()
        normalized[key] = v
    return normalized

def get_forex_action(field, system_type):
    """Get the appropriate action for forex discrepancies"""
    actions = {
        "FO-FO": {
            "fxrate": "Confirm correct FX rate from execution logs and align both FO systems.",
            "notionalamount": "Verify trade notional. Contact support if unclear or trade is disputed.",
            "buy/sell": "Validate trade direction; correct side or mail trader for confirmation.",
            "instrument": "Check currency pair mapping. Contact ops team if unclear.",
            "producttype": "Review product classification; mail booking desk if mismatch persists."
        },
        "FO-BO": {
            "settlementdate": "Confirm market convention (e.g., T+1) and update system. Contact BO team if needed.",
            "valuedate": "Confirm market convention (e.g., T+1) and update system. Contact BO team if needed.",
            "fxrate": "Verify applied FX rate. Escalate via email if BO and FO differ persistently.",
            "notionalamount": "Confirm deal size from trade capture. Contact settlements team if mismatch unresolved.",
            "buy/sell": "Cross-check trade side. Contact trade owner if discrepancy remains.",
            "instrument": "Validate FX pair legs; escalate to booking support if mismatched.",
            "producttype": "Recheck trade type. Notify risk team if classification seems invalid."
        }
    }
    return actions.get(system_type, {}).get(field, "No action required")

def save_reconciliation_results_to_firebase(results, system_type):
    db = get_firestore_client()
    collection_name = f"fx_reconciliation_{system_type.replace('-', '')}"
    for result in results:
        trade_id = result.get("TradeID")
        if trade_id:
            db.collection(collection_name).document(str(trade_id)).set(result)

def reconcile_trades(system_type, save_to_firebase=False):
    try:
        results = []

        if system_type == "FO-FO":
            system_a, system_b = load_trades_fofo()
            # Normalize all trade dicts
            system_a = [normalize_dict_keys(a) for a in system_a]
            system_b = [normalize_dict_keys(b) for b in system_b]
            for a in system_a:
                for b in system_b:
                    if a.get("tradeid") == b.get("tradeid"):
                        discrepancies = []
                        compare_fields = [
                            ("fxrate", "FX Rate mismatch"),
                            ("notionalamount", "Notional Amount mismatch"),
                            ("buy/sell", "Buy/Sell mismatch"),
                            ("instrument", "Currency Pair mismatch"),
                            ("producttype", "Product Type mismatch")
                        ]
                        for field, reason in compare_fields:
                            a_val = a.get(field)
                            b_val = b.get(field)
                            if a_val != b_val:
                                discrepancies.append({
                                    "field": field,
                                    "systemA": a_val,
                                    "systemB": b_val,
                                    "reason": reason,
                                    "action": get_forex_action(field, "FO-FO")
                                })
                        if discrepancies:
                            results.append({
                                "TradeID": a.get("tradeid"),
                                "SystemA": a,
                                "SystemB": b,
                                "discrepancies": discrepancies
                            })
                        else:
                            # Add a result for matched trades too
                            results.append({
                                "TradeID": a.get("tradeid"),
                                "SystemA": a,
                                "SystemB": b,
                                "discrepancies": []
                            })

        elif system_type == "FO-BO":
            front, back = load_trades_fobo()
            front = [normalize_dict_keys(f) for f in front]
            back = [normalize_dict_keys(b) for b in back]
            for f in front:
                for b in back:
                    if f.get("tradeid") == b.get("tradeid"):
                        discrepancies = []
                        compare_fields = [
                            ("settlementdate", "Settlement date mismatch"),
                            ("valuedate", "Value date mismatch"),
                            ("fxrate", "FX Rate mismatch"),
                            ("notionalamount", "Notional Amount mismatch"),
                            ("buy/sell", "Buy/Sell mismatch"),
                            ("instrument", "Currency Pair mismatch"),
                            ("producttype", "Product Type mismatch")
                        ]
                        for field, reason in compare_fields:
                            f_val = f.get(field)
                            b_val = b.get(field)
                            if f_val != b_val:
                                discrepancies.append({
                                    "field": field,
                                    "frontOffice": f_val,
                                    "backOffice": b_val,
                                    "reason": reason,
                                    "action": get_forex_action(field, "FO-BO")
                                })
                        if discrepancies:
                            results.append({
                                "TradeID": f.get("tradeid"),
                                "FrontOffice": f,
                                "BackOffice": b,
                                "discrepancies": discrepancies
                            })
                        else:
                            results.append({
                                "TradeID": f.get("tradeid"),
                                "FrontOffice": f,
                                "BackOffice": b,
                                "discrepancies": []
                            })

        if save_to_firebase:
            save_reconciliation_results_to_firebase(results, system_type)

        return results
    except Exception as e:
        logging.exception("Error in reconcile_trades")
        return {"error": str(e)}
