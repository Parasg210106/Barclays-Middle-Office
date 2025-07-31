from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict
from datetime import datetime
from services.equity_trade_validation.services.validation_runner import validate_trades
from services.equity_capture.db.trade_repository import trade_repository
from services.equity_termsheet_capture.db.termsheet_repository import load_termsheets
from services.firebase_client import get_firestore_client
from services.equity_trade_validation.core.rules_config import rules_config

router = APIRouter()

def assign_department_based_on_failures(reasons):
    """Assign department based on validation failure reasons"""
    if not reasons:
        return "NA"
    
    # Get department assignment rules
    dept_rules = rules_config.get("department_assignment", {})
    
    # Check each failure reason against department rules
    for reason in reasons:
        for dept, fields in dept_rules.items():
            for field in fields:
                if field in reason:
                    return dept
    
    return "NA"

@router.post('/validate')
def validate(captured_trades: list = Body(...), termsheet: list = Body(...)):
    return validate_trades(captured_trades, termsheet)

@router.get('/validation-results')
def get_validation_results():
    # Load all trades and termsheets
    print("🔍 Loading trades and termsheets for validation...")
    trades = [t.dict() for t in trade_repository.load_trades()]
    print(f"   Loaded {len(trades)} trades")
    
    termsheets = load_termsheets()
    print(f"   Loaded {len(termsheets)} termsheets from Firebase")
    
    if trades:
        print(f"   First trade keys: {list(trades[0].keys())}")
        print(f"   First trade Trade ID: {trades[0].get('TradeID') or trades[0].get('Trade ID')}")
    
    if termsheets:
        print(f"   First termsheet keys: {list(termsheets[0].keys())}")
        print(f"   First termsheet Trade ID: {termsheets[0].get('Trade ID') or termsheets[0].get('TradeID')}")
    
    # Check for matching Trade IDs
    trade_ids = set()
    for trade in trades:
        trade_id = trade.get('TradeID') or trade.get('Trade ID')
        if trade_id:
            trade_ids.add(str(trade_id).strip())
    
    termsheet_ids = set()
    for termsheet in termsheets:
        termsheet_id = termsheet.get('Trade ID') or termsheet.get('TradeID')
        if termsheet_id:
            termsheet_ids.add(str(termsheet_id).strip())
    
    print(f"   Trade IDs from trades: {sorted(list(trade_ids))}")
    print(f"   Trade IDs from termsheets: {sorted(list(termsheet_ids))}")
    
    matches = trade_ids.intersection(termsheet_ids)
    print(f"   Matching Trade IDs: {sorted(list(matches))}")
    
    # Run validation
    results = validate_trades(trades, termsheets)
    print(f"   Validation completed with {len(results)} results")
    
    # Count statuses
    pending_count = sum(1 for r in results if r['status'] == 'Pending')
    failed_count = sum(1 for r in results if r['status'] == 'Failed')
    success_count = sum(1 for r in results if r['status'] == 'Success')
    
    print(f"   Status summary: Success={success_count}, Failed={failed_count}, Pending={pending_count}")
    
    # Store validation results in Firebase
    db = get_firestore_client()
    for result in results:
        if result["TradeID"]:
            # Assign department based on failure reasons
            assigned_dept = assign_department_based_on_failures(result.get("reasons", []))
            
            # Create document for Firebase storage
            validation_doc = {
                "TradeID": result["TradeID"],
                "ValidationStatus": ("Validated" if result["status"] == "Success" else "Failed") if result["status"] != "Pending" else "Pending",
                "ValidationErrors": result.get("reasons", []),
                "AssignedTo": assigned_dept,
                "validation_timestamp": datetime.now().isoformat()
            }
            # Store in eq_validation collection
            db.collection("eq_validation").document(str(result["TradeID"])).set(validation_doc)
    
    # Return TradeID, status, and assigned department for frontend
    return [{
        "TradeID": r["TradeID"], 
        "status": ("Validated" if r["status"] == "Success" else "Failed") if r["status"] != "Pending" else "Pending",
        "AssignedTo": assign_department_based_on_failures(r.get("reasons", []))
    } for r in results]

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
