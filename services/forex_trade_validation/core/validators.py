import re
from datetime import datetime, timedelta
from services.forex_trade_validation.core.rules_config import (
    MANDATORY_FIELDS, VALID_CURRENCIES, VALID_CURRENCY_PAIRS, VALID_PRODUCT_TYPES,
    VALID_BUY_SELL, VALID_KYC_STATUS, VALID_COUNTERPARTIES,
    MIN_NOTIONAL_AMOUNT, MAX_NOTIONAL_AMOUNT, MAX_FX_RATE, MAX_SETTLEMENT_DAYS,
    validate_date_format, validate_float_format, validate_currency_code,
    validate_currency_pair, validate_enum_format,
    validate_date_sequence, validate_numeric_ranges,
    validate_spot_trade_settlement, validate_forward_maturity,
    validate_currency_pair_consistency,
    validate_counterparty, validate_kyc_status, validate_product_type_flags
)

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
            elif not validate_date_format(value):
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
            elif not validate_float_format(value):
                errors.append(f"Invalid float in field: {field}")
        
        elif expected_type == "currency_code":
            if value is None:
                errors.append(f"Missing currency code in field: {field}")
            elif not validate_currency_code(value):
                errors.append(f"Invalid currency code in field: {field}. Expected one of {VALID_CURRENCIES}")
        
        elif expected_type == "currency_pair":
            if value is None:
                errors.append(f"Missing currency pair in field: {field}")
            elif not validate_currency_pair(value):
                errors.append(f"Invalid currency pair in field: {field}. Expected one of {VALID_CURRENCY_PAIRS}")
        
        elif isinstance(expected_type, list):
            if value not in expected_type:
                errors.append(f"Invalid value '{value}' for field: {field}. Expected: {expected_type}")
    
    return errors

# -----------------------------
# Logical Rule Check
# -----------------------------
def check_logical_rules(trade: dict) -> list:
    errors = []

    # Date sequence validation
    if all(trade.get(field) for field in ["TradeDate", "SettlementDate", "MaturityDate"]):
        date_errors = validate_date_sequence(
            trade["TradeDate"], 
            trade["SettlementDate"], 
            trade["MaturityDate"]
        )
        errors.extend(date_errors)

    # Numeric range validation
    if trade.get("NotionalAmount") and trade.get("FXRate"):
        try:
            numeric_errors = validate_numeric_ranges(
                float(trade["NotionalAmount"]), 
                float(trade["FXRate"])
            )
            errors.extend(numeric_errors)
        except (ValueError, TypeError):
            errors.append("Invalid numeric values for range validation")

    return errors

# -----------------------------
# Business Rules Check
# -----------------------------
def check_business_rules(trade: dict) -> list:
    errors = []

    # Spot trade settlement validation
    if trade.get("TradeDate") and trade.get("SettlementDate") and trade.get("ProductType"):
        spot_errors = validate_spot_trade_settlement(
            trade["TradeDate"], 
            trade["SettlementDate"], 
            trade["ProductType"]
        )
        errors.extend(spot_errors)

    # Forward maturity validation
    if trade.get("TradeDate") and trade.get("MaturityDate") and trade.get("ProductType"):
        forward_errors = validate_forward_maturity(
            trade["TradeDate"], 
            trade["MaturityDate"], 
            trade["ProductType"]
        )
        errors.extend(forward_errors)

    # Currency pair consistency validation
    if trade.get("CurrencyPair") and trade.get("DealtCurrency") and trade.get("BaseCurrency"):
        currency_errors = validate_currency_pair_consistency(
            trade["CurrencyPair"], 
            trade["DealtCurrency"], 
            trade["BaseCurrency"]
        )
        errors.extend(currency_errors)

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

# -----------------------------
# Enhanced Validation Functions
# -----------------------------
def check_counterparty_validation(trade: dict) -> list:
    """Enhanced counterparty validation"""
    if trade.get("Counterparty"):
        return validate_counterparty(trade["Counterparty"])
    return []

def check_kyc_validation(trade: dict) -> list:
    """Enhanced KYC validation"""
    if trade.get("KYCCheck"):
        return validate_kyc_status(trade["KYCCheck"])
    return []

def check_product_type_validation(trade: dict) -> list:
    """Enhanced product type validation with flags"""
    if trade.get("ProductType"):
        return validate_product_type_flags(trade["ProductType"])
    return []

# -----------------------------
# Comprehensive Validation
# -----------------------------
def validate_forex_trade_comprehensive(trade: dict) -> dict:
    """
    Comprehensive validation function that uses all validation rules
    """
    errors = []
    warnings = []

    # 1. Mandatory field validation
    errors.extend(check_mandatory_fields(trade, MANDATORY_FIELDS))

    # 2. Format validation
    format_rules = {
        "TradeDate": "date",
        "MaturityDate": "date", 
        "SettlementDate": "date",
        "NotionalAmount": "float",
        "FXRate": "float",
        "BuySell": VALID_BUY_SELL,
        "ProductType": VALID_PRODUCT_TYPES,
        "KYCCheck": VALID_KYC_STATUS,
        "CurrencyPair": "currency_pair",
        "DealtCurrency": "currency_code",
        "BaseCurrency": "currency_code",
        "TermCurrency": "currency_code"
    }
    errors.extend(check_format_rules(trade, format_rules))

    # 3. Logical validation
    errors.extend(check_logical_rules(trade))

    # 4. Business rules validation
    errors.extend(check_business_rules(trade))

    # 5. Static validation
    static_config = {
        "CurrencyPair": VALID_CURRENCY_PAIRS,
        "DealtCurrency": VALID_CURRENCIES,
        "BaseCurrency": VALID_CURRENCIES,
        "TermCurrency": VALID_CURRENCIES,
        "ProductType": VALID_PRODUCT_TYPES,
        "KYCCheck": VALID_KYC_STATUS,
        "Counterparty": VALID_COUNTERPARTIES
    }
    errors.extend(check_static_values(trade, static_config))

    # 6. Enhanced custom validation
    errors.extend(check_counterparty_validation(trade))
    errors.extend(check_kyc_validation(trade))
    errors.extend(check_product_type_validation(trade))

    # 7. Custom rules from config
    custom_rules = [
        {
            "field": "Counterparty",
            "condition": "== 'Unknown'",
            "action": "flag_manual_review"
        },
        {
            "field": "KYCCheck",
            "condition": "!= 'Complete'",
            "action": "flag_kyc_incomplete"
        },
        {
            "field": "FXRate",
            "condition": "<= 0",
            "action": "flag_invalid_fx_rate"
        },
        {
            "field": "NotionalAmount",
            "condition": "<= 0",
            "action": "flag_invalid_notional"
        }
    ]
    errors.extend(check_custom_rules(trade, custom_rules))

    return {
        "TradeID": trade.get("TradeID", "UNKNOWN"),
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "validation_timestamp": datetime.now().isoformat()
    }
