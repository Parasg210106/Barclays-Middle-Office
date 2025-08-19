from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from services.forex_trade_validation.services.validation_runner import ValidationRunner
from services.firebase_client import get_firestore_client
from datetime import datetime
import re
from services.forex_trade_validation.core.rules_config import load_rules_config
rules_config = load_rules_config()
department_assignment = rules_config.get('department_assignment', {})

router = APIRouter()
validation_runner = ValidationRunner()

class TradeValidationRequest(BaseModel):
    trades: List[Dict]

class SingleTradeValidationRequest(BaseModel):
    trade: Dict

def normalize_value(field, value):
    if value is None:
        return None
    if field in ["NotionalAmount", "FXRate"]:
        try:
            return float(value)
        except Exception:
            return value
    if field in ["TradeDate", "MaturityDate", "SettlementDate"]:
        # Try to parse as date, fallback to string
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"):
            try:
                return datetime.strptime(str(value), fmt).date()
            except Exception:
                continue
        return str(value).strip()
    return str(value).strip()

def extract_field_from_error(error):
    match = re.match(r"^([A-Za-z0-9_]+) mismatch:", error)
    if match:
        return match.group(1)
    return error.split(' ')[0]

def assign_department(errors):
    if not errors:
        return 'NA'
    for dept, fields in department_assignment.items():
        for error in errors:
            field = extract_field_from_error(error)
            if field in fields:
                return dept
    return 'NA'

@router.post("/validate")
async def validate_trades(request: TradeValidationRequest):
    """
    Validate a list of trades using the Forex validation rules.
    """
    try:
        results = validation_runner.validate_trades(request.trades)
        return {
            "message": "Validation completed",
            "results": results,
            "summary": validation_runner.get_validation_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.post("/validate/single")
async def validate_single_trade(request: SingleTradeValidationRequest):
    """
    Validate a single trade.
    """
    try:
        result = validation_runner.validate_single_trade(request.trade)
        return {
            "message": "Single trade validation completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.get("/results")
async def get_validation_results():
    """
    Get all validation results.
    """
    try:
        results = validation_runner.repository.get_all_validated_trades()
        return {
            "results": results,
            "summary": validation_runner.get_validation_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")

@router.get("/results/failed")
async def get_failed_trades():
    """
    Get all trades that failed validation.
    """
    try:
        failed_trades = validation_runner.get_failed_trades()
        return {
            "failed_trades": failed_trades,
            "count": len(failed_trades)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving failed trades: {str(e)}")

@router.get("/results/passed")
async def get_passed_trades():
    """
    Get all trades that passed validation.
    """
    try:
        passed_trades = validation_runner.get_passed_trades()
        return {
            "passed_trades": passed_trades,
            "count": len(passed_trades)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving passed trades: {str(e)}")

@router.get("/summary")
async def get_validation_summary():
    """
    Get a summary of validation results.
    """
    try:
        summary = validation_runner.get_validation_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving summary: {str(e)}")

@router.get("/trade/{trade_id}")
async def get_trade_by_id(trade_id: str):
    """
    Get validation result for a specific trade by ID.
    """
    try:
        trade = validation_runner.repository.get_trade_by_id(trade_id)
        if trade:
            return trade
        else:
            raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trade: {str(e)}")

@router.delete("/clear")
async def clear_validation_data():
    """
    Clear all validation data from the database.
    """
    try:
        success = validation_runner.clear_validation_data()
        if success:
            return {"message": "Validation data cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear validation data")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "service": "forex_trade_validation"}

@router.get("/debug-collections")
async def debug_collections():
    """
    Debug endpoint to check what's in the fx_capture and fx_validation collections.
    """
    try:
        db = get_firestore_client()
        
        # Check fx_capture collection
        fx_capture_docs = list(db.collection("fx_capture").stream())
        print(f"[DEBUG] fx_capture collection has {len(fx_capture_docs)} documents")
        
        # Check fx_validation collection
        fx_validation_docs = list(db.collection("fx_validation").stream())
        print(f"[DEBUG] fx_validation collection has {len(fx_validation_docs)} documents")
        
        # Check fx_termsheet collection
        fx_termsheet_docs = list(db.collection("fx_termsheet").stream())
        print(f"[DEBUG] fx_termsheet collection has {len(fx_termsheet_docs)} documents")
        
        return {
            "fx_capture_count": len(fx_capture_docs),
            "fx_validation_count": len(fx_validation_docs),
            "fx_termsheet_count": len(fx_termsheet_docs),
            "fx_capture_sample": [doc.to_dict() for doc in fx_capture_docs[:2]] if fx_capture_docs else [],
            "fx_validation_sample": [doc.to_dict() for doc in fx_validation_docs[:2]] if fx_validation_docs else [],
            "fx_termsheet_sample": [doc.to_dict() for doc in fx_termsheet_docs[:2]] if fx_termsheet_docs else []
        }
        
    except Exception as e:
        print(f"[DEBUG] Error in debug_collections: {str(e)}")
        return {"error": str(e)}

@router.get("/get-validation-status")
async def get_validation_status():
    """
    Get the current validation status for all trades from the fx_validation collection.
    This endpoint retrieves existing validation results without running validation again.
    """
    try:
        db = get_firestore_client()
        validation_docs = list(db.collection("fx_validation").stream())
        
        print(f"[DEBUG] Found {len(validation_docs)} validation documents in fx_validation collection")
        
        results = []
        for doc in validation_docs:
            doc_data = doc.to_dict()
            print(f"[DEBUG] Processing validation doc: {doc.id} with data: {doc_data}")
            
            results.append({
                "TradeID": doc_data.get("TradeID", ""),
                "TraderID": doc_data.get("TraderID", ""),
                "Currency": doc_data.get("Currency", ""),
                "TradeDate": doc_data.get("TradeDate", ""),
                "KYCStatus": doc_data.get("KYCStatus", ""),
                "ValidationStatus": doc_data.get("ValidationStatus", "Pending"),
                "ValidationErrors": doc_data.get("ValidationErrors", []),
                "AssignedTo": doc_data.get("AssignedTo", "NA"),
                "Actions": "View Termsheet"
            })
        
        print(f"[DEBUG] Returning {len(results)} validation results")
        return {"results": results}
        
    except Exception as e:
        print(f"[DEBUG] Error in get_validation_status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving validation status: {str(e)}")

@router.get("/validate-forex-capture")
async def validate_forex_capture():
    """
    Fetch all trades from fx_capture, validate against fx_termsheet, and return validation results for frontend table.
    Only the essential parameters are compared.
    Also store the validation status and mismatch reasons in Firestore under 'fx_validation'.
    """
    try:
        db = get_firestore_client()
        trades = [doc.to_dict() for doc in db.collection("fx_capture").stream()]
        termsheets = {doc.id: doc.to_dict() for doc in db.collection("fx_termsheet").stream()}
        # Only these fields are required for validation
        essential_fields = [
            "TradeDate", "Counterparty", "CurrencyPair", "BuySell", "DealtCurrency", "BaseCurrency", "TermCurrency", "NotionalAmount", "FXRate", "ProductType", "MaturityDate", "SettlementDate", "KYCCheck"
        ]
        results = []
        for trade in trades:
            trade_id = trade.get("TradeID")
            termsheet = termsheets.get(trade_id)
            errors = []
            if not termsheet:
                errors.append(f"No termsheet found for TradeID {trade_id}")
            else:
                for field in essential_fields:
                    trade_value = normalize_value(field, trade.get(field))
                    termsheet_value = normalize_value(field, termsheet.get(field))
                    if trade_value != termsheet_value:
                        errors.append(f"{field} mismatch: trade='{trade_value}' vs termsheet='{termsheet_value}'")
            validation_status = "Passed" if not errors else "Failed"
            assigned_to = assign_department(errors) if validation_status == "Failed" else "NA"
            result_doc = {
                "TradeID": trade.get("TradeID", ""),
                "TraderID": trade.get("TraderID", ""),
                "Currency": trade.get("CurrencyPair", ""),
                "TradeDate": trade.get("TradeDate", ""),
                "KYCStatus": trade.get("KYCCheck", ""),
                "ValidationStatus": validation_status,
                "ValidationErrors": errors,
                "AssignedTo": assigned_to
            }
            # Store in Firestore under fx_validation
            if trade_id:
                db.collection("fx_validation").document(str(trade_id)).set(result_doc)
            results.append({
                **result_doc,
                "Actions": "View Termsheet"
            })
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.get("/overview-stats")
async def get_overview_stats():
    """Get overview statistics for the dashboard cards"""
    try:
        db = get_firestore_client()

        
        # Card 1: Total trades in validation (equity + forex combined)
        total_trades = 0
        
        # Count equity trades
        equity_trades = list(db.collection('trades').stream())
        total_trades += len(equity_trades)

        
        # Count forex trades
        forex_trades = list(db.collection('fx_capture').stream())
        total_trades += len(forex_trades)

        
        # Card 2: Pending lifecycle trades (equity + forex combined)
        lifecycle_trades = 0
        
        # Count pending equity lifecycle trades
        for trade in equity_trades:
            trade_data = trade.to_dict()
            # Check if trade is pending (not approved)
            if trade_data.get('ApprovalStatus') != 'Approved':
                lifecycle_trades += 1
        
        # Count pending forex lifecycle trades
        for trade in forex_trades:
            trade_data = trade.to_dict()
            # Check if trade is pending (not approved)
            if trade_data.get('ApprovalStatus') != 'Approved':
                lifecycle_trades += 1
        

        
        # Card 3: Trades with discrepancies from reconciliation page (exclude "no discrepancy" trades)
        reconciliation_breaks = 0
        
        # Count equity reconciliation breaks (trades with discrepancies)
        equity_reconciliation = list(db.collection('equity_reconciliation').stream())
        for reconciliation in equity_reconciliation:
            reconciliation_data = reconciliation.to_dict()
            # Check if there are discrepancies (exclude "no discrepancy")
            if reconciliation_data.get('REASON') and reconciliation_data.get('REASON') != 'no discrepancy':
                reconciliation_breaks += 1
        
        # Count forex reconciliation breaks (trades with discrepancies) - FOFO and FOBO
        forex_reconciliation_fofo = list(db.collection('fx_reconciliation_FOFO').stream())
        for reconciliation in forex_reconciliation_fofo:
            reconciliation_data = reconciliation.to_dict()
            # Check if there are discrepancies (exclude "no discrepancy")
            if reconciliation_data.get('REASON') and reconciliation_data.get('REASON') != 'no discrepancy':
                reconciliation_breaks += 1
        
        forex_reconciliation_fobo = list(db.collection('fx_reconciliation_FOBO').stream())
        for reconciliation in forex_reconciliation_fobo:
            reconciliation_data = reconciliation.to_dict()
            # Check if there are discrepancies (exclude "no discrepancy")
            if reconciliation_data.get('REASON') and reconciliation_data.get('REASON') != 'no discrepancy':
                reconciliation_breaks += 1
        

        
        return {
            "total_trades": total_trades,
            "lifecycle_events_pending": lifecycle_trades,
            "reconciliation_breaks": reconciliation_breaks
        }
        
    except Exception as e:

        return {
            "total_trades": 0,
            "lifecycle_events_pending": 0,
            "reconciliation_breaks": 0
        } 