from typing import List
from fastapi import APIRouter, HTTPException
from shared.models import Trade
from services.equity_capture.services.capture_service import trade_capture_service
import json
import os
from services.equity_capture.db.trade_repository import trade_repository

router = APIRouter()

@router.post("/trades", response_model=Trade)
async def capture_trade(trade: Trade):
    try:
        return trade_capture_service.add_trade(trade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trades/bulk", response_model=List[Trade])
async def bulk_capture_trades(trades: List[Trade]):
    results = []
    errors = []
    for trade in trades:
        try:
            results.append(trade_capture_service.add_trade(trade))
        except ValueError as e:
            errors.append({"trade_id": trade.trade_id, "error": str(e)})
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    return results

@router.get("/trades")
def get_trades():
    return [t.dict() for t in trade_repository.load_trades()]

@router.get("/trades/{trade_id}", response_model=Trade)
async def get_trade(trade_id: str):
    trade = trade_capture_service.get_trade(trade_id)
    if trade:
        return trade
    raise HTTPException(status_code=404, detail="Trade not found")

@router.post("/test/create-sample-trade")
async def create_sample_trade():
    """Create a sample trade for testing purposes"""
    try:
        from shared.models import Trade
        
        # Create a sample trade
        sample_trade = Trade(
            trade_id="TEST001",
            order_id="ORD001",
            client_id="CLIENT001",
            isin="US0378331005",
            symbol="AAPL",
            trade_type="BUY",
            quantity=100,
            price=150.00,
            trade_value=15000.00,
            currency="USD",
            trade_date="2024-01-15",
            settlement_date="2024-01-17",
            settlement_status="PENDING",
            counterparty="BROKER001",
            trading_venue="NASDAQ",
            trader_name="John Doe",
            kyc_status="APPROVED",
            reference_data_validated="YES",
            commission=15.00,
            taxes=0.00,
            total_cost=15015.00,
            confirmation_status="CONFIRMED",
            country_of_trade="US",
            ops_team_notes="Sample trade for testing",
            pricing_source="BLOOMBERG",
            market_impact_cost=0.00,
            fx_rate_applied=1.00,
            net_amount=15000.00,
            collateral_required=0.00,
            margin_type="NONE",
            margin_status="NONE"
        )
        
        # Save the trade
        trade_repository.save_trade(sample_trade)
        
        print(f"[DEBUG] Created sample trade with client_id: {sample_trade.client_id}")
        return {"message": "Sample trade created", "trade_id": sample_trade.trade_id, "client_id": sample_trade.client_id}
        
    except Exception as e:
        print(f"[DEBUG] Error creating sample trade: {str(e)}")
        return {"error": str(e)}

@router.get("/debug/collections")
async def debug_collections():
    """Debug endpoint to check Firebase collections and data"""
    try:
        db = trade_repository.db
        
        # List all collections
        collections = [col.id for col in db.collections()]
        print(f"[DEBUG] Available collections: {collections}")
        
        # Check trades collection specifically
        trades_collection = db.collection("trades")
        trades_count = len(list(trades_collection.stream()))
        print(f"[DEBUG] Trades collection has {trades_count} documents")
        
        # Get first few trades as sample
        sample_trades = []
        for doc in trades_collection.limit(3).stream():
            sample_trades.append(doc.to_dict())
        
        return {
            "collections": collections,
            "trades_count": trades_count,
            "sample_trades": sample_trades
        }
    except Exception as e:
        print(f"[DEBUG] Error in debug_collections: {str(e)}")
        return {"error": str(e)}

@router.get("/client-ids")
async def get_client_ids():
    """Get list of unique client IDs from unified_data collection with ClientID_Forex field"""
    try:
        db = trade_repository.db
        
        # Get client IDs specifically from unified_data collection
        unified_collection = db.collection("unified_data")
        docs = list(unified_collection.stream())
        print(f"[DEBUG] Found {len(docs)} documents in unified_data collection")
        
        client_ids = []
        for doc in docs:
            doc_data = doc.to_dict()
            # Get ClientID_Forex field specifically
            client_id = doc_data.get('ClientID_Forex')
            if client_id and client_id not in client_ids:
                client_ids.append(client_id)
        
        print(f"[DEBUG] Found {len(client_ids)} unique ClientID_Forex values: {client_ids}")
        return {"client_ids": client_ids}
    except Exception as e:
        print(f"[DEBUG] Error in get_client_ids: {str(e)}")
        return {"client_ids": [], "error": str(e)}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Firebase connection
        db = trade_repository.db
        collections = [col.id for col in db.collections()]
        
        return {
            "status": "ok",
            "firebase_connected": True,
            "available_collections": collections,
            "timestamp": "2024-01-15T12:00:00Z"
        }
    except Exception as e:
        return {
            "status": "error",
            "firebase_connected": False,
            "error": str(e),
            "timestamp": "2024-01-15T12:00:00Z"
        } 