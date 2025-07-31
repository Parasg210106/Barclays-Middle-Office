def check_trade_type_mismatch(a, b):
    return a.get("Trade Type") != b.get("Trade Type")

def check_quantity_mismatch(a, b):
    return int(a.get("Quantity", 0)) != int(b.get("Quantity", 0))

def check_symbol_mismatch(a, b):
    return a.get("Symbol") != b.get("Symbol")

def check_price_mismatch(a, b):
    return float(a.get("Price", 0)) != float(b.get("Price", 0))

def check_trade_value_mismatch(a, b):
    return float(a.get("Trade Value", 0)) != float(b.get("Trade Value", 0))

def check_settlement_date_mismatch(a, b):
    return a.get("Settlement Date") != b.get("Settlement Date")
