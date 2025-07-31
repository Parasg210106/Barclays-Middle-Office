from typing import List
from fastapi import APIRouter, HTTPException
from services.forex_capture.models import Forex
from services.forex_capture.services.capture_service import forex_capture_service
import json
import os
from services.forex_capture.db.forex_repository import forex_repository
try:
    from services.firebase_client import get_firestore_client
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Warning: Firebase client not available")

router = APIRouter()

def normalize_csv_data(data: dict) -> dict:
    """
    Normalize CSV data to handle spacing and minor variations in column names.
    This ensures robust mapping from CSV to the Forex model.
    """
    normalized = {}
    
    # Add debugging to see what columns we're receiving
    print(f"[DEBUG] Received CSV columns: {list(data.keys())}")
    
    # Define mapping from common variations to exact model aliases
    column_mapping = {
        # Handle common spacing variations
        "counterparty_id": "Counterparty ID",
        "counterparty id": "Counterparty ID",
        "CounterpartyID": "Counterparty ID",
        "custodian_name": "Custodian_Name",
        "custodian name": "Custodian_Name",
        "CustodianName": "Custodian_Name",
        "exception_type": "Exception Type",
        "exception type": "Exception Type",
        "ExceptionType": "Exception Type",
        "exception_description": "Exception Description",
        "exception description": "Exception Description",
        "ExceptionDescription": "Exception Description",
        "exception_resolution": "Exception Resolution",
        "exception resolution": "Exception Resolution",
        "ExceptionResolution": "Exception Resolution",
        "reporting_regulation": "Reporting Regulation",
        "reporting regulation": "Reporting Regulation",
        "ReportingRegulation": "Reporting Regulation",
        "exception_reason": "Exception Reason",
        "exception reason": "Exception Reason",
        "ExceptionReason": "Exception Reason",
        "reporting_resolution": "Reporting Resolution",
        "reporting resolution": "Reporting Resolution",
        "ReportingResolution": "Reporting Resolution",
        "trading_venue": "Trading Venue",
        "trading venue": "Trading Venue",
        "TradingVenue": "Trading Venue",
        "country_of_trade": "Country_of_Trade",
        "country of trade": "Country_of_Trade",
        "CountryOfTrade": "Country_of_Trade",
        "instrument_status": "Instrument_Status",
        "instrument status": "Instrument_Status",
        "InstrumentStatus": "Instrument_Status",
        "clientid_equity": "ClientID_Equity",
        "client id equity": "ClientID_Equity",
        "ClientIDEquity": "ClientID_Equity",
        "kyc_status_equity": "KYC_Status_Equity",
        "kyc status equity": "KYC_Status_Equity",
        "KYCStatusEquity": "KYC_Status_Equity",
        "reference_data_validated": "Reference_Data_Validated",
        "reference data validated": "Reference_Data_Validated",
        "ReferenceDataValidated": "Reference_Data_Validated",
        "margin_type": "Margin_Type",
        "margin type": "Margin_Type",
        "MarginType": "Margin_Type",
        "margin_status": "Margin_Status",
        "margin status": "Margin_Status",
        "MarginStatus": "Margin_Status",
        "client_approval_status_equity": "Client_Approval_Status_Equity",
        "client approval status equity": "Client_Approval_Status_Equity",
        "ClientApprovalStatusEquity": "Client_Approval_Status_Equity",
        "clientid_forex": "ClientID_Forex",
        "client id forex": "ClientID_Forex",
        "ClientIDForex": "ClientID_Forex",
        "kyc_status_forex": "KYC_Status_Forex",
        "kyc status forex": "KYC_Status_Forex",
        "KYCStatusForex": "KYC_Status_Forex",
        "expense_approval_status": "Expense_Approval_Status",
        "expense approval status": "Expense_Approval_Status",
        "ExpenseApprovalStatus": "Expense_Approval_Status",
        "client_approval_status_forex": "Client Approval Status(forex)",
        "client approval status forex": "Client Approval Status(forex)",
        "ClientApprovalStatusForex": "Client Approval Status(forex)",
        "custodian_ac_no": "Custodian_Ac_no",
        "custodian ac no": "Custodian_Ac_no",
        "CustodianAcNo": "Custodian_Ac_no",
        "beneficiary_client_id": "Beneficiary_Client_ID",
        "beneficiary client id": "Beneficiary_Client_ID",
        "BeneficiaryClientID": "Beneficiary_Client_ID",
        "settlement_cycle": "Settlement_Cycle",
        "settlement cycle": "Settlement_Cycle",
        "SettlementCycle": "Settlement_Cycle",
        "effectivedate_equity": "EffectiveDate_Equity",
        "effective date equity": "EffectiveDate_Equity",
        "EffectiveDateEquity": "EffectiveDate_Equity",
        "confirmationstatus_equity": "ConfirmationStatus_Equity",
        "confirmation status equity": "ConfirmationStatus_Equity",
        "ConfirmationStatusEquity": "ConfirmationStatus_Equity",
        "swift_equity": "SWIFT_Equity",
        "swift equity": "SWIFT_Equity",
        "SwiftEquity": "SWIFT_Equity",
        "beneficiaryname_equity": "BeneficiaryName_Equity",
        "beneficiary name equity": "BeneficiaryName_Equity",
        "BeneficiaryNameEquity": "BeneficiaryName_Equity",
        
        # Enhanced Account Number mappings for Equity
        "account_number_equity": "Account_Number_Equity",
        "account number equity": "Account_Number_Equity",
        "AccountNumberEquity": "Account_Number_Equity",
        "account_equity": "Account_Number_Equity",
        "accountequity": "Account_Number_Equity",
        "account_equity_number": "Account_Number_Equity",
        "equity_account_number": "Account_Number_Equity",
        "equityaccountnumber": "Account_Number_Equity",
        
        "aba_equity": "ABA_Equity",
        "ABAEquity": "ABA_Equity",
        "aba_equit": "ABA_Equity",  # Handle truncated version
        "bsb_equity": "BSB_Equity",
        "BSBEquity": "BSB_Equity",
        "bsb_equit": "BSB_Equity",  # Handle truncated version
        "iban_equity": "IBAN_Equity",
        "IBANEquity": "IBAN_Equity",
        "iban_equ": "IBAN_Equity",  # Handle truncated version
        "sort_equity": "SORT_Equity",
        "SortEquity": "SORT_Equity",
        "sort_equ": "SORT_Equity",  # Handle truncated version
        "zengin_equity": "Zengin_Equity",
        "ZenginEquity": "Zengin_Equity",
        "zengin_eq": "Zengin_Equity",  # Handle truncated version
        "settlement_method_equity": "Settlement_Method_Equity",
        "settlement method equity": "Settlement_Method_Equity",
        "SettlementMethodEquity": "Settlement_Method_Equity",
        "settlemen": "Settlement_Method_Equity",  # Handle truncated version
        
        "effectivedate_forex": "EffectiveDate_Forex",
        "effective date forex": "EffectiveDate_Forex",
        "EffectiveDateForex": "EffectiveDate_Forex",
        "effectived": "EffectiveDate_Forex",  # Handle truncated version
        "confirmationstatus_forex": "ConfirmationStatus_Forex",
        "confirmation status forex": "ConfirmationStatus_Forex",
        "ConfirmationStatusForex": "ConfirmationStatus_Forex",
        "confirmat": "ConfirmationStatus_Forex",  # Handle truncated version
        
        # Enhanced Account Number mappings for Forex
        "account_number_forex": "Account Number_Forex",
        "account number forex": "Account Number_Forex",
        "AccountNumberForex": "Account Number_Forex",
        "account_forex": "Account Number_Forex",
        "accountforex": "Account Number_Forex",
        "account_forex_number": "Account Number_Forex",
        "forex_account_number": "Account Number_Forex",
        "forexaccountnumber": "Account Number_Forex",
        "account number_forex": "Account Number_Forex",  # Handle space variation
        
        "swift_forex": "SWIFT_Forex",
        "swift forex": "SWIFT_Forex",
        "SwiftForex": "SWIFT_Forex",
        "beneficiaryname_forex": "BeneficiaryName_Forex",
        "beneficiary name forex": "BeneficiaryName_Forex",
        "BeneficiaryNameForex": "BeneficiaryName_Forex",
        "aba_forex": "ABA_Forex",
        "ABAForex": "ABA_Forex",
        "bsb_forex": "BSB_Forex",
        "BSBForex": "BSB_Forex",
        "iban_forex": "IBAN_Forex",
        "IBANForex": "IBAN_Forex",
        "sort_forex": "SORT_Forex",
        "SortForex": "SORT_Forex",
        "zengin_forex": "Zengin_Forex",
        "ZenginForex": "Zengin_Forex",
        "settlement_method_forex": "Settlement_Method_Forex",
        "settlement method forex": "Settlement_Method_Forex",
        "SettlementMethodForex": "Settlement_Method_Forex",
    }
    
    for key, value in data.items():
        # Normalize the key (remove extra spaces, convert to lowercase for comparison)
        normalized_key = key.strip().lower()
        
        # Add debugging for specific fields we're looking for
        if "account" in normalized_key or "equity" in normalized_key or "forex" in normalized_key:
            print(f"[DEBUG] Processing key: '{key}' -> normalized: '{normalized_key}' -> value: '{value}'")
        
        # Check if we have a mapping for this key
        if normalized_key in column_mapping:
            mapped_key = column_mapping[normalized_key]
            normalized[mapped_key] = value
            print(f"[DEBUG] Mapped '{key}' -> '{mapped_key}' with value '{value}'")
        else:
            # If no mapping, use the original key (but strip spaces)
            normalized[key.strip()] = value
            print(f"[DEBUG] No mapping found for '{key}', using original key")
    
    print(f"[DEBUG] Final normalized keys: {list(normalized.keys())}")
    return normalized

@router.post("/forex", response_model=Forex)
async def add_forex(forex: Forex):
    try:
        # Check for duplicate in Firestore
        if forex_repository.get_forex(forex.TradeID):
            raise HTTPException(status_code=400, detail=f"TradeID '{forex.TradeID}' already exists")
        forex_repository.save_forex(forex)
        return forex
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/forexs/bulk", response_model=List[Forex])
async def bulk_capture_forexs(forexs_data: List[dict]):
    results = []
    errors = []
    
    print(f"[DEBUG] Received {len(forexs_data)} trades for bulk processing")
    
    for i, forex_data in enumerate(forexs_data):
        try:
            print(f"[DEBUG] Processing trade {i+1}/{len(forexs_data)}")
            print(f"[DEBUG] Raw trade data: {forex_data}")
            
            # Check if TradeID is present and not empty
            trade_id = forex_data.get("TradeID", "").strip()
            if not trade_id:
                errors.append({
                    "TradeID": "EMPTY", 
                    "error": "TradeID is required and cannot be empty"
                })
                continue
            
            # Normalize the data to handle column name variations
            normalized_data = normalize_csv_data(forex_data)
            
            # Debug: Print the normalized data before creating Forex object
            print(f"[DEBUG] Normalized data for TradeID {trade_id}: {normalized_data}")
            
            # Create Forex object from normalized data
            try:
                forex = Forex.parse_obj(normalized_data)
                print(f"[DEBUG] Forex object created successfully for TradeID {trade_id}")
            except Exception as parse_error:
                print(f"[DEBUG] Error parsing Forex object for TradeID {trade_id}: {parse_error}")
                errors.append({"TradeID": trade_id, "error": f"Parsing error: {str(parse_error)}"})
                continue
            
            # Debug: Print the Forex object after parsing
            print(f"[DEBUG] Forex object created for TradeID {trade_id}:")
            print(f"[DEBUG] Account_Number_Equity: '{forex.Account_Number_Equity}'")
            print(f"[DEBUG] Account_Number_Forex: '{forex.Account_Number_Forex}'")
            print(f"[DEBUG] ABA_Equity: '{forex.ABA_Equity}'")
            print(f"[DEBUG] BSB_Equity: '{forex.BSB_Equity}'")
            print(f"[DEBUG] Settlement_Method_Equity: '{forex.Settlement_Method_Equity}'")
            
            if forex_repository.get_forex(forex.TradeID):
                raise Exception(f"TradeID '{forex.TradeID}' already exists")
            forex_repository.save_forex(forex)
            results.append(forex)
        except Exception as e:
            print(f"[DEBUG] Error processing trade {i+1}: {str(e)}")
            errors.append({"TradeID": forex_data.get("TradeID", "Unknown"), "error": str(e)})
    
    print(f"[DEBUG] Processing complete. Results: {len(results)}, Errors: {len(errors)}")
    
    if errors:
        print(f"[DEBUG] Errors found: {errors}")
        raise HTTPException(status_code=400, detail=errors)
    return results

@router.get("/forexs")
def get_forexs():
    print("[DEBUG] /forexs route called")
    return [f.dict() for f in forex_repository.load_forexs()]

@router.get("/forexs/{TradeID}", response_model=Forex)
async def get_forex(TradeID: str):
    forex = forex_capture_service.get_forex(TradeID)
    if forex:
        return forex
    raise HTTPException(status_code=404, detail="Forex not found")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@router.get("/test-overview")
async def test_overview():
    """Simple test endpoint"""
    return {"message": "Test overview endpoint works"}

@router.get("/overview-stats")
async def get_overview_stats():
    """Get overview statistics for the dashboard cards"""
    try:
        if not FIREBASE_AVAILABLE:
            print("Debug: Firebase not available, returning default values")
            return {
                "total_trades": 0,
                "lifecycle_events_pending": 0,
                "reconciliation_breaks": 0
            }
        
        db = get_firestore_client()
        print("Debug: Starting overview stats calculation")
        
        # Card 1: Total trades in validation (equity + forex combined)
        total_trades = 0
        
        # Count equity trades
        equity_trades = list(db.collection('trades').stream())
        total_trades += len(equity_trades)
        print(f"Debug: Found {len(equity_trades)} equity trades")
        
        # Count forex trades
        forex_trades = list(db.collection('fx_capture').stream())
        total_trades += len(forex_trades)
        print(f"Debug: Found {len(forex_trades)} forex trades")
        print(f"Debug: Total trades (Card 1): {total_trades}")
        
        # Card 2: Lifecycle events (trades in lifecycle collection minus trades in capture collection)
        lifecycle_trades = 0
        
        # Count trades in lifecycle collections
        equity_lifecycle = list(db.collection('equity_lifecycle').stream())
        forex_lifecycle = list(db.collection('fx_lifecycle').stream())
        total_lifecycle = len(equity_lifecycle) + len(forex_lifecycle)
        
        # Total trades in capture collections
        total_capture = len(equity_trades) + len(forex_trades)
        
                    # Lifecycle events = capture trades - lifecycle trades
        lifecycle_trades = total_capture - total_lifecycle
        if lifecycle_trades < 0:
                lifecycle_trades = 0  # Don't show negative numbers
        
        print(f"Debug: Equity lifecycle trades: {len(equity_lifecycle)}")
        print(f"Debug: Forex lifecycle trades: {len(forex_lifecycle)}")
        print(f"Debug: Total lifecycle trades: {total_lifecycle}")
        print(f"Debug: Total capture trades: {total_capture}")
        print(f"Debug: Lifecycle events (Card 2): {lifecycle_trades}")
        
        # Card 3: Trades with discrepancies from reconciliation page (check discrepancy array)
        reconciliation_breaks = 0
        
        # Count equity reconciliation breaks (trades with discrepancies)
        equity_reconciliation = list(db.collection('equity_reconciliation').stream())
        for reconciliation in equity_reconciliation:
            reconciliation_data = reconciliation.to_dict()
            # Check if discrepancies array has any data (note: it's "discrepancies" not "discrepancy")
            discrepancies_array = reconciliation_data.get('discrepancies', [])
            if discrepancies_array and len(discrepancies_array) > 0:
                reconciliation_breaks += 1
                print(f"Debug: Found equity reconciliation break with {len(discrepancies_array)} discrepancies")
        
        # Count forex reconciliation breaks (trades with discrepancies) - FOFO and FOBO
        forex_reconciliation_fofo = list(db.collection('fx_reconciliation_FOFO').stream())
        for reconciliation in forex_reconciliation_fofo:
            reconciliation_data = reconciliation.to_dict()
            # Check if discrepancies array has any data (note: it's "discrepancies" not "discrepancy")
            discrepancies_array = reconciliation_data.get('discrepancies', [])
            if discrepancies_array and len(discrepancies_array) > 0:
                reconciliation_breaks += 1
                print(f"Debug: Found FOFO reconciliation break with {len(discrepancies_array)} discrepancies")
        
        forex_reconciliation_fobo = list(db.collection('fx_reconciliation_FOBO').stream())
        for reconciliation in forex_reconciliation_fobo:
            reconciliation_data = reconciliation.to_dict()
            # Check if discrepancies array has any data (note: it's "discrepancies" not "discrepancy")
            discrepancies_array = reconciliation_data.get('discrepancies', [])
            if discrepancies_array and len(discrepancies_array) > 0:
                reconciliation_breaks += 1
                print(f"Debug: Found FOBO reconciliation break with {len(discrepancies_array)} discrepancies")
        
        print(f"Debug: Reconciliation breaks (Card 3): {reconciliation_breaks}")
        print(f"Debug: Final stats - Total: {total_trades}, Lifecycle: {lifecycle_trades}, Breaks: {reconciliation_breaks}")
        
        return {
            "total_trades": total_trades,
            "lifecycle_events_pending": lifecycle_trades,
            "reconciliation_breaks": reconciliation_breaks
        }
        
    except Exception as e:
        print(f"Error fetching overview stats: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            "total_trades": 0,
            "lifecycle_events_pending": 0,
            "reconciliation_breaks": 0
        }