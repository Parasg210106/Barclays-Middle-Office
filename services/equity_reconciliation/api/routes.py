from fastapi import APIRouter
from services.equity_reconciliation.services.reconciliation_service import reconcile_trades
from services.firebase_client import get_firestore_client

router = APIRouter()

@router.get("/reconcile/{system_type}")
def reconcile(system_type: str, save_to_firebase: bool = True):
    print(f"Equity reconcile endpoint called with system_type={system_type}, save_to_firebase={save_to_firebase}")
    result = reconcile_trades(system_type)
    
    if save_to_firebase:
        # Save results to Firebase based on reconciliation type
        db = get_firestore_client()
        collection_name = f"eq_reconciliation_{system_type.replace('-', '')}"
        print(f"Saving equity reconciliation results to collection: {collection_name}")
        
        for item in result:
            trade_id = item.get("TradeID", "unknown")
            db.collection(collection_name).document(trade_id).set(item)
    
    print(f"Equity reconcile result: {result}")
    return {"reconciliation_result": result}
