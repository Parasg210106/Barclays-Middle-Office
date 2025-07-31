from services.equity_reconciliation.db.trade_repository import load_trades
from services.equity_reconciliation.core import rules

def get_equity_action(discrepancy, system_type):
    """Get the appropriate action for equity reconciliation discrepancies"""
    action_map = {
        "FO-FO": {
            "Symbol mismatch": "Verify stock symbol; contact front office support if mapping issue.",
            "Trade Type mismatch": "Reconfirm order direction. Mail trader for clarification if inconsistent.",
            "Quantity mismatch": "Cross-verify order quantity with trade confirmation. Contact booking desk if unclear.",
            "Price mismatch": "Validate execution price; escalate via email if price source differs.",
            "Trade value mismatch": "Recalculate value (Qty × Price); contact FO platform support if misaligned."
        },
        "FO-BO": {
            "Symbol mismatch": "Check security identifier mapping. Raise ticket if not consistent.",
            "Trade Type mismatch": "Validate Buy/Sell direction. Escalate to FO if trade logic is incorrect.",
            "Quantity mismatch": "Compare FO quantity with clearing data. Mail settlements team if mismatch persists.",
            "Price mismatch": "Confirm execution price from broker blotter. Contact back office if discrepancy remains.",
            "Trade value mismatch": "Reconfirm value computation. Escalate to accounting if incorrect.",
            "Settlement date mismatch": "Validate correct T+ cycle. Mail BO team if settlement logic differs."
        }
    }
    
    if discrepancy == "No discrepancy":
        return "No action required"
    
    return action_map.get(system_type, {}).get(discrepancy, "Review and escalate as needed.")

def reconcile_trades(system_type):
    trades = load_trades()
    results = []

    if system_type == "FO-FO":
        system_a = [t for t in trades if t["Source"] == "SystemA"]
        system_b = [t for t in trades if t["Source"] == "SystemB"]

        for a in system_a:
            for b in system_b:
                if a["Trade ID"] == b["Trade ID"]:
                    discrepancies = []
                    if rules.check_trade_type_mismatch(a, b):
                        discrepancies.append("Trade Type mismatch")
                    if rules.check_quantity_mismatch(a, b):
                        discrepancies.append("Quantity mismatch")
                    if rules.check_symbol_mismatch(a, b):
                        discrepancies.append("Symbol mismatch")
                    if rules.check_price_mismatch(a, b):
                        discrepancies.append("Price mismatch")
                    if rules.check_trade_value_mismatch(a, b):
                        discrepancies.append("Trade value mismatch")

                    # Format System A data
                    system_a_formatted = f"{a.get('Trade Type', 'N/A')} {a.get('Quantity', 'N/A')} shares of {a.get('Symbol', 'N/A')} at {a.get('Price', 'N/A')} each, totalling to a trade value of {a.get('Trade Value', 'N/A')}."
                    
                    # Format System B data
                    system_b_formatted = f"{b.get('Trade Type', 'N/A')} {b.get('Quantity', 'N/A')} shares of {b.get('Symbol', 'N/A')} at {b.get('Price', 'N/A')} each, totalling to a trade value of {b.get('Trade Value', 'N/A')}."
                    
                    # Get actions for each discrepancy
                    actions = []
                    for discrepancy in discrepancies:
                        action = get_equity_action(discrepancy, "FO-FO")
                        actions.append(f"{discrepancy}: {action}")
                    
                    if not discrepancies:
                        actions = ["No action required"]
                    
                    results.append({
                        "TradeID": a["Trade ID"],
                        "SystemA": system_a_formatted,
                        "SystemB": system_b_formatted,
                        "SystemARaw": a,
                        "SystemBRaw": b,
                        "Discrepancy": discrepancies or ["No discrepancy"],
                        "Action": actions
                    })

    elif system_type == "FO-BO":
        front = [t for t in trades if t["Source"] == "FrontOffice"]
        back = [t for t in trades if t["Source"] == "BackOffice"]

        for f in front:
            for b in back:
                if f["Trade ID"] == b["Trade ID"]:
                    discrepancies = []
                    if rules.check_trade_type_mismatch(f, b):
                        discrepancies.append("Trade Type mismatch")
                    if rules.check_quantity_mismatch(f, b):
                        discrepancies.append("Quantity mismatch")
                    if rules.check_symbol_mismatch(f, b):
                        discrepancies.append("Symbol mismatch")
                    if rules.check_price_mismatch(f, b):
                        discrepancies.append("Price mismatch")
                    if rules.check_trade_value_mismatch(f, b):
                        discrepancies.append("Trade value mismatch")
                    if rules.check_settlement_date_mismatch(f, b):
                        discrepancies.append("Settlement date mismatch")

                    # Format Front Office data
                    front_office_formatted = f"{f.get('Trade Type', 'N/A')} {f.get('Quantity', 'N/A')} shares of {f.get('Symbol', 'N/A')} at {f.get('Price', 'N/A')} each, totalling to a trade value of {f.get('Trade Value', 'N/A')}, to be settled on {f.get('Settlement Date', 'N/A')}."
                    
                    # Format Back Office data
                    back_office_formatted = f"{b.get('Trade Type', 'N/A')} {b.get('Quantity', 'N/A')} shares of {b.get('Symbol', 'N/A')} at {b.get('Price', 'N/A')} each, totalling to a trade value of {b.get('Trade Value', 'N/A')}, to be settled on {b.get('Settlement Date', 'N/A')}."
                    
                    # Get actions for each discrepancy
                    actions = []
                    for discrepancy in discrepancies:
                        action = get_equity_action(discrepancy, "FO-BO")
                        actions.append(f"{discrepancy}: {action}")
                    
                    if not discrepancies:
                        actions = ["No action required"]
                    
                    results.append({
                        "TradeID": f["Trade ID"],
                        "FrontOffice": front_office_formatted,
                        "BackOffice": back_office_formatted,
                        "FrontOfficeRaw": f,
                        "BackOfficeRaw": b,
                        "Discrepancy": discrepancies or ["No discrepancy"],
                        "Action": actions
                    })

    return results
