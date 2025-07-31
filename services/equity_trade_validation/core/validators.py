import re
from datetime import datetime

# -----------------------------
# Mandatory Field Check
# -----------------------------
def check_mandatory_fields(trade: dict, mandatory_fields: list) -> list:
    errors = []
    for field in mandatory_fields:
        if field not in trade or str(trade[field]).strip() == "":
            errors.append(f"Missing mandatory field: {field}")
    return errors

# -----------------------------
# Format Validation
# -----------------------------
def check_format_rules(trade: dict, format_rules: dict) -> list:
    errors = []
    for field, expected_type in format_rules.items():
        value = trade.get(field)

        if expected_type == "date":
            if value is None:
                errors.append(f"Missing date in field: {field}")
            else:
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except Exception:
                    errors.append(f"Invalid date format in field: {field} (Expected YYYY-MM-DD)")
        
        elif expected_type == "int":
            if value is None:
                errors.append(f"Missing integer in field: {field}")
            elif not isinstance(value, int):
                try:
                    int(value)
                except:
                    errors.append(f"Invalid integer in field: {field}")
        
        elif expected_type == "float":
            if value is None:
                errors.append(f"Missing float in field: {field}")
            elif not isinstance(value, float):
                try:
                    float(value)
                except:
                    errors.append(f"Invalid float in field: {field}")
        
        elif expected_type == "isin":
            if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', str(value)):
                errors.append(f"Invalid ISIN format in field: {field}")
        
        elif isinstance(expected_type, list):
            if value not in expected_type:
                errors.append(f"Invalid value '{value}' for field: {field}. Expected: {expected_type}")
    
    return errors

# -----------------------------
# Logical Rule Check
# -----------------------------
def check_logical_rules(trade: dict) -> list:
    errors = []

    try:
        trade_date = datetime.strptime(trade["Trade Date"], "%Y-%m-%d")
        settlement_date = datetime.strptime(trade["Settlement Date"], "%Y-%m-%d")
        if settlement_date < trade_date:
            errors.append("Settlement Date is earlier than Trade Date")
    except:
        errors.append("Invalid or missing date fields for logical comparison")

    try:
        quantity = float(trade["Quantity"])
        price = float(trade["Price"])
        trade_value = float(trade["Trade Value"])
        if round(quantity * price, 2) != round(trade_value, 2):
            errors.append("Trade Value ≠ Quantity * Price")
    except:
        errors.append("Invalid numeric values for Quantity, Price or Trade Value")

    try:
        total_cost = float(trade["Total Cost"])
        commission = float(trade["Commission"])
        taxes = float(trade["Taxes"])
        expected_cost = float(trade["Trade Value"]) + commission + taxes
        if round(expected_cost, 2) != round(total_cost, 2):
            errors.append("Total Cost ≠ Trade Value + Commission + Taxes")
    except:
        errors.append("Invalid values for cost calculation")

    return errors

# -----------------------------
# Static Value Validation
# -----------------------------
def check_static_values(trade: dict, static_config: dict) -> list:
    errors = []
    for field, valid_values in static_config.items():
        if trade.get(field) not in valid_values:
            errors.append(f"Invalid value in field: {field}. Expected one of {valid_values}")
    return errors

# -----------------------------
# Custom Rule Check
# -----------------------------
def check_custom_rules(trade: dict, custom_rules: list) -> list:
    errors = []
    for rule in custom_rules:
        field = rule["field"]
        condition = rule["condition"]
        action = rule["action"]

        try:
            value = trade.get(field)
            expr = f'"{value}" {condition}' if isinstance(value, str) else f'{value} {condition}'
            if eval(expr):
                errors.append(f"{action}: Rule violated on field {field} with condition {condition}")
        except Exception as e:
            errors.append(f"Error evaluating custom rule on field {field}: {str(e)}")

    return errors
