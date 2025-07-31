"""
Forex Trade Validation Rules Configuration
Defines comprehensive validation rules for all 13 Forex parameters
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
import json
import os

# ============================================================================
# CONSTANTS
# ============================================================================

# Valid Currency Codes
VALID_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD", "SGD", "HKD"
]

# Valid Currency Pairs
VALID_CURRENCY_PAIRS = [
    "USD/EUR", "EUR/USD", "USD/GBP", "GBP/USD", "USD/JPY", "JPY/USD", 
    "EUR/GBP", "GBP/EUR", "USD/CHF", "CHF/USD", "USD/CAD", "CAD/USD",
    "AUD/USD", "USD/AUD", "NZD/USD", "USD/NZD", "EUR/JPY", "JPY/EUR",
    "GBP/JPY", "JPY/GBP", "EUR/CHF", "CHF/EUR", "GBP/CHF", "CHF/GBP"
]

# Valid Product Types
VALID_PRODUCT_TYPES = ["Spot", "Forward", "Swap", "Option", "NDF"]

# Valid Buy/Sell Values
VALID_BUY_SELL = ["Buy", "Sell"]

# Valid KYC Status Values
VALID_KYC_STATUS = ["Complete", "Incomplete", "Pending", "Rejected"]

# Valid Counterparties
VALID_COUNTERPARTIES = [
    "Goldman Sachs", "JP Morgan", "Morgan Stanley", "Citigroup", "Bank of America",
    "Deutsche Bank", "UBS", "Credit Suisse", "Barclays", "HSBC", "BNP Paribas",
    "Societe Generale", "RBC", "TD Securities", "CIBC", "Scotiabank"
]

# Business Limits
MIN_NOTIONAL_AMOUNT = 1000
MAX_NOTIONAL_AMOUNT = 1000000000
MAX_FX_RATE = 1000
MAX_SETTLEMENT_DAYS = 30

# ============================================================================
# MANDATORY FIELDS
# ============================================================================

MANDATORY_FIELDS = [
    "TradeID", "TradeDate", "Counterparty", "CurrencyPair", "BuySell", 
    "DealtCurrency", "BaseCurrency", "TermCurrency", "NotionalAmount", 
    "FXRate", "ProductType", "MaturityDate", "SettlementDate", "KYCCheck"
]

# ============================================================================
# FORMAT VALIDATION RULES
# ============================================================================

def validate_date_format(value: str) -> bool:
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False

def validate_float_format(value: Any) -> bool:
    """Validate float format"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def validate_currency_code(value: str) -> bool:
    """Validate currency code format"""
    return value in VALID_CURRENCIES

def validate_currency_pair(value: str) -> bool:
    """Validate currency pair format"""
    return value in VALID_CURRENCY_PAIRS

def validate_enum_format(value: str, valid_values: List[str]) -> bool:
    """Validate enum format"""
    return value in valid_values

# ============================================================================
# LOGICAL VALIDATION RULES
# ============================================================================

def validate_date_sequence(trade_date: str, settlement_date: str, maturity_date: str) -> List[str]:
    """Validate date sequence logic"""
    errors = []
    
    try:
        trade_dt = datetime.strptime(trade_date, "%Y-%m-%d")
        settlement_dt = datetime.strptime(settlement_date, "%Y-%m-%d")
        maturity_dt = datetime.strptime(maturity_date, "%Y-%m-%d")
        today = datetime.now().date()
        
        # Trade date cannot be in the future
        if trade_dt.date() > today:
            errors.append("Trade date cannot be in the future")
        
        # Settlement date must be >= trade date
        if settlement_dt < trade_dt:
            errors.append("Settlement date must not be before trade date")
        
        # Maturity date must be >= trade date
        if maturity_dt < trade_dt:
            errors.append("Maturity date must not be before trade date")
        
        # Maturity date must be >= settlement date
        if maturity_dt < settlement_dt:
            errors.append("Maturity date must not be before settlement date")
        
        # Settlement date cannot be more than 30 days in the future
        max_settlement = today + timedelta(days=MAX_SETTLEMENT_DAYS)
        if settlement_dt.date() > max_settlement:
            errors.append(f"Settlement date cannot be more than {MAX_SETTLEMENT_DAYS} days in the future")
            
    except (ValueError, TypeError):
        errors.append("Invalid date format for date sequence validation")
    
    return errors

def validate_numeric_ranges(notional_amount: float, fx_rate: float) -> List[str]:
    """Validate numeric value ranges"""
    errors = []
    
    # FX Rate validation
    if fx_rate <= 0:
        errors.append("FX Rate must be positive")
    elif fx_rate > MAX_FX_RATE:
        errors.append(f"FX Rate must be reasonable (<= {MAX_FX_RATE})")
    
    # Notional Amount validation
    if notional_amount <= 0:
        errors.append("Notional amount must be positive")
    elif notional_amount < MIN_NOTIONAL_AMOUNT:
        errors.append(f"Notional amount must be at least {MIN_NOTIONAL_AMOUNT}")
    elif notional_amount > MAX_NOTIONAL_AMOUNT:
        errors.append(f"Notional amount must not exceed {MAX_NOTIONAL_AMOUNT}")
    
    return errors

# ============================================================================
# BUSINESS RULES
# ============================================================================

def validate_spot_trade_settlement(trade_date: str, settlement_date: str, product_type: str) -> List[str]:
    """Validate spot trade settlement (T+2)"""
    errors = []
    
    if product_type == "Spot":
        try:
            trade_dt = datetime.strptime(trade_date, "%Y-%m-%d")
            settlement_dt = datetime.strptime(settlement_date, "%Y-%m-%d")
            expected_settlement = trade_dt + timedelta(days=2)
            
            if settlement_dt.date() != expected_settlement.date():
                errors.append("Spot trades must settle T+2 (TradeDate + 2 days)")
                
        except (ValueError, TypeError):
            errors.append("Invalid date format for spot settlement validation")
    
    return errors

def validate_forward_maturity(trade_date: str, maturity_date: str, product_type: str) -> List[str]:
    """Validate forward trade maturity"""
    errors = []
    
    if product_type == "Forward":
        try:
            trade_dt = datetime.strptime(trade_date, "%Y-%m-%d")
            maturity_dt = datetime.strptime(maturity_date, "%Y-%m-%d")
            
            if maturity_dt <= trade_dt:
                errors.append("Forward trades must have a future maturity date")
                
        except (ValueError, TypeError):
            errors.append("Invalid date format for forward maturity validation")
    
    return errors

def validate_currency_pair_consistency(currency_pair: str, dealt_currency: str, base_currency: str) -> List[str]:
    """Validate currency pair consistency with dealt/base currencies"""
    errors = []
    
    if currency_pair and dealt_currency and base_currency:
        expected_pair = f"{dealt_currency}/{base_currency}"
        if currency_pair != expected_pair:
            errors.append(f"Currency pair '{currency_pair}' must match dealt/base currency combination '{expected_pair}'")
    
    return errors

# ============================================================================
# CUSTOM VALIDATION RULES
# ============================================================================

def validate_counterparty(counterparty: str) -> List[str]:
    """Validate counterparty"""
    errors = []
    
    if not counterparty:
        errors.append("Counterparty is mandatory")
    elif counterparty == "Unknown":
        errors.append("flag_manual_review: Unknown counterparty requires manual review")
    elif counterparty not in VALID_COUNTERPARTIES:
        errors.append("flag_unknown_counterparty: Counterparty not in approved list")
    
    return errors

def validate_kyc_status(kyc_status: str) -> List[str]:
    """Validate KYC status"""
    errors = []
    
    if not kyc_status:
        errors.append("KYC status is mandatory")
    elif kyc_status == "Incomplete":
        errors.append("flag_kyc_incomplete: KYC verification incomplete")
    elif kyc_status == "Rejected":
        errors.append("flag_kyc_rejected: KYC verification rejected")
    elif kyc_status == "Pending":
        errors.append("flag_kyc_pending: KYC verification pending")
    elif kyc_status not in VALID_KYC_STATUS:
        errors.append(f"Invalid KYC status: {kyc_status}")
    
    return errors

def validate_product_type_flags(product_type: str) -> List[str]:
    """Validate product type and set appropriate flags"""
    errors = []
    
    if product_type == "Option":
        errors.append("flag_option_trade: Option trade requires special handling")
    elif product_type == "NDF":
        errors.append("flag_ndf_trade: NDF trade requires special handling")
    elif product_type not in VALID_PRODUCT_TYPES:
        errors.append(f"Invalid product type: {product_type}")
    
    return errors

# ============================================================================
# COMPREHENSIVE VALIDATION FUNCTION
# ============================================================================

def validate_forex_trade(trade: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive validation function for Forex trades
    
    Args:
        trade: Dictionary containing trade data
        
    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []
    
    # 1. Mandatory field validation
    for field in MANDATORY_FIELDS:
        if field not in trade or str(trade.get(field, "")).strip() == "":
            errors.append(f"Missing mandatory field: {field}")
    
    # 2. Format validation
    if trade.get("TradeDate"):
        if not validate_date_format(trade["TradeDate"]):
            errors.append("Invalid TradeDate format (expected YYYY-MM-DD)")
    
    if trade.get("SettlementDate"):
        if not validate_date_format(trade["SettlementDate"]):
            errors.append("Invalid SettlementDate format (expected YYYY-MM-DD)")
    
    if trade.get("MaturityDate"):
        if not validate_date_format(trade["MaturityDate"]):
            errors.append("Invalid MaturityDate format (expected YYYY-MM-DD)")
    
    if trade.get("NotionalAmount"):
        if not validate_float_format(trade["NotionalAmount"]):
            errors.append("Invalid NotionalAmount format")
    
    if trade.get("FXRate"):
        if not validate_float_format(trade["FXRate"]):
            errors.append("Invalid FXRate format")
    
    if trade.get("CurrencyPair"):
        if not validate_currency_pair(trade["CurrencyPair"]):
            errors.append(f"Invalid CurrencyPair: {trade['CurrencyPair']}")
    
    if trade.get("DealtCurrency"):
        if not validate_currency_code(trade["DealtCurrency"]):
            errors.append(f"Invalid DealtCurrency: {trade['DealtCurrency']}")
    
    if trade.get("BaseCurrency"):
        if not validate_currency_code(trade["BaseCurrency"]):
            errors.append(f"Invalid BaseCurrency: {trade['BaseCurrency']}")
    
    if trade.get("TermCurrency"):
        if not validate_currency_code(trade["TermCurrency"]):
            errors.append(f"Invalid TermCurrency: {trade['TermCurrency']}")
    
    if trade.get("BuySell"):
        if not validate_enum_format(trade["BuySell"], VALID_BUY_SELL):
            errors.append(f"Invalid BuySell: {trade['BuySell']}")
    
    if trade.get("ProductType"):
        if not validate_enum_format(trade["ProductType"], VALID_PRODUCT_TYPES):
            errors.append(f"Invalid ProductType: {trade['ProductType']}")
    
    # 3. Logical validation
    if all(trade.get(field) for field in ["TradeDate", "SettlementDate", "MaturityDate"]):
        date_errors = validate_date_sequence(
            trade["TradeDate"], 
            trade["SettlementDate"], 
            trade["MaturityDate"]
        )
        errors.extend(date_errors)
    
    if trade.get("NotionalAmount") and trade.get("FXRate"):
        try:
            numeric_errors = validate_numeric_ranges(
                float(trade["NotionalAmount"]), 
                float(trade["FXRate"])
            )
            errors.extend(numeric_errors)
        except (ValueError, TypeError):
            errors.append("Invalid numeric values for range validation")
    
    # 4. Business rules validation
    if trade.get("TradeDate") and trade.get("SettlementDate") and trade.get("ProductType"):
        spot_errors = validate_spot_trade_settlement(
            trade["TradeDate"], 
            trade["SettlementDate"], 
            trade["ProductType"]
        )
        errors.extend(spot_errors)
    
    if trade.get("TradeDate") and trade.get("MaturityDate") and trade.get("ProductType"):
        forward_errors = validate_forward_maturity(
            trade["TradeDate"], 
            trade["MaturityDate"], 
            trade["ProductType"]
        )
        errors.extend(forward_errors)
    
    if trade.get("CurrencyPair") and trade.get("DealtCurrency") and trade.get("BaseCurrency"):
        currency_errors = validate_currency_pair_consistency(
            trade["CurrencyPair"], 
            trade["DealtCurrency"], 
            trade["BaseCurrency"]
        )
        errors.extend(currency_errors)
    
    # 5. Custom validation
    if trade.get("Counterparty"):
        counterparty_errors = validate_counterparty(trade["Counterparty"])
        errors.extend(counterparty_errors)
    
    if trade.get("KYCCheck"):
        kyc_errors = validate_kyc_status(trade["KYCCheck"])
        errors.extend(kyc_errors)
    
    if trade.get("ProductType"):
        product_errors = validate_product_type_flags(trade["ProductType"])
        errors.extend(product_errors)
    
    # 6. Return validation result
    return {
        "TradeID": trade.get("TradeID", "UNKNOWN"),
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "validation_timestamp": datetime.now().isoformat()
    }

def load_rules_config():
    config_path = os.path.join(os.path.dirname(__file__), "rules_config.json")
    with open(config_path, "r") as f:
        return json.load(f)

# ============================================================================
# FIELD DESCRIPTIONS
# ============================================================================

FIELD_DESCRIPTIONS = {
    "TradeDate": "Date when the trade was executed (YYYY-MM-DD format)",
    "Counterparty": "The other party in the trade transaction",
    "CurrencyPair": "The currency pair being traded (e.g., USD/EUR)",
    "BuySell": "Whether the trade is a buy or sell transaction",
    "DealtCurrency": "The currency being bought or sold",
    "BaseCurrency": "The base currency in the pair",
    "TermCurrency": "The term currency in the pair",
    "NotionalAmount": "The notional amount of the trade",
    "FXRate": "The foreign exchange rate for the trade",
    "ProductType": "Type of forex product (Spot, Forward, Swap, Option, NDF)",
    "MaturityDate": "Date when the trade matures (YYYY-MM-DD format)",
    "SettlementDate": "Date when the trade settles (YYYY-MM-DD format)",
    "KYCCheck": "Know Your Customer verification status"
}

# ============================================================================
# VALIDATION PRIORITIES
# ============================================================================

VALIDATION_PRIORITIES = {
    "critical": ["TradeID", "TradeDate", "Counterparty", "CurrencyPair", "NotionalAmount", "FXRate"],
    "high": ["BuySell", "ProductType", "SettlementDate", "KYCCheck"],
    "medium": ["DealtCurrency", "BaseCurrency", "TermCurrency", "MaturityDate"]
}
