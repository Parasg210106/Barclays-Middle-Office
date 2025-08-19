from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
import pandas as pd
from datetime import datetime
import uuid
import json
import math
from services.trade_lifecycle.main import load_trades, filter_trades_by_event, save_filtered_trades
from services.trade_lifecycle.core.maturity_logic import get_maturity_trades, approve_maturity_trade
from services.trade_lifecycle.core.coupon_logic import get_coupon_trades, approve_coupon_trade, pay_coupon
from services.trade_lifecycle.core.early_redemption_logic import get_early_redemption_trades, get_early_redemption_trade, mark_trade_redeemed, parse_date
import logging
import numpy as np
from services.equity_capture.db.trade_repository import trade_repository
from services.forex_capture.db.forex_repository import forex_repository
from shared.models import Trade
from services.forex_capture.models import Forex
from services.firebase_client import get_firestore_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

logger.info("ROUTES FILE LOADED")

EVENTS = [
    ("Early-Redemption", "Early Redemption"),
    ("Barrier-Monitoring", "Barrier Monitoring"),
    ("Coupon Rate", "Coupon Rate"),
    ("Maturity", "Maturity")
]

DISPLAY_COLUMNS = [
    "Trade ID", "Order ID", "Symbol", "Trade Type", "Quantity", "Price", "Trade Value", "event_type"
]

CONSOLIDATED_COLUMNS = [
    "Trade ID", "Trader ID", "Currency", "Trade Date", "KYC Status", "Validation Status",
    "BuySell", "NotionalAmount", "FXRate", "SettlementDate", "Approval Status",
    "INTERNAL VALUE", "EXTERNAL VALUE", "REPORTEDTO", "REASON"
]

def clean_for_json(obj):
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj

@router.get("/", response_class=HTMLResponse)
def overview(request: Request):
    allowed_filenames = set()
    for event in EVENTS:
        base = event[0]
        allowed_filenames.add(f"{base}.csv")
        allowed_filenames.add(f"{base.replace('_', ' ')}.csv")
        allowed_filenames.add(f"{base.replace(' ', '_')}.csv")
    files = []
    for filename in os.listdir("filtered_trades"):
        if filename in allowed_filenames:
            files.append({
                'filename': filename,
                'download_url': f"/filtered_trades/{filename}"
            })
    return templates.TemplateResponse("overview.html", {"request": request, "files": files, "events": EVENTS})

@router.post("/upload", response_class=HTMLResponse)
def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        upload_id = str(uuid.uuid4())
        file_location = f"data/{upload_id}_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        df = load_trades(file_location)
        filtered = filter_trades_by_event(df, event_column='event_type')
        save_filtered_trades(filtered)
        os.remove(file_location)

        # Store only the trades that would be displayed in the lifecycle tab
        firestore_db = get_firestore_client()
        for event, trades_df in filtered.items():
            for row in trades_df.to_dict(orient="records"):
                # Decide which repository to use based on TradeType or TradeID
                trade_id = str(row.get('Trade ID', '') or row.get('TradeID', ''))
                trade_type = row.get('Trade Type', '') or row.get('TradeType', '')
                
                # Apply the same filtering logic as the lifecycle tab
                # 1. Instrument filter - only upload Forex trades to fx_lifecycle
                is_forex_trade = trade_id.upper().startswith('FX') or trade_type.upper() == 'FOREX'
                
                # 2. Event type filter - only upload trades with valid event types
                valid_event_types = ['Maturity', 'Coupon Rate', 'Early Redemption', 'Barrier Monitoring']
                event_type_normalized = event.replace('-', ' ').title()
                is_valid_event = event_type_normalized in valid_event_types
                
                # Debug: Log the original row data
                logger.info(f"Processing row for trade {trade_id}: {row}")
                
                # Only upload to fx_lifecycle if it's a Forex trade with a valid event type
                if is_forex_trade and is_valid_event:
                    # --- Store in fx_lifecycle collection ---
                    lifecycle_doc_id = f"{trade_id}_{event}" if trade_id else str(uuid.uuid4())
                    
                    # Only store the specific fields that are displayed in the lifecycle tab
                    lifecycle_data = {
                        'TradeID': trade_id,
                        'CurrencyPair': row.get('CurrencyPair', ''),
                        'Symbol': row.get('Symbol', ''),
                        'EventType': event,
                        'event_type': event,
                        'EventDate': row.get('MaturityDate', row.get('SettlementDate', row.get('TradeDate', ''))),
                        'TradeDate': row.get('TradeDate', ''),
                        'EventStatus': 'Pending',  # Default status
                        'FXRate': row.get('FXRate', ''),
                        'NotionalAmount': row.get('NotionalAmount', ''),
                        'SettlementDate': row.get('SettlementDate', ''),
                        'BuySell': row.get('BuySell', ''),
                        'ApprovalStatus': 'Pending',  # Default status
                        'uploaded_at': datetime.utcnow().isoformat()
                    }
                    
                    try:
                        firestore_db.collection('fx_lifecycle').document(lifecycle_doc_id).set(lifecycle_data)
                        logger.info(f"Stored trade lifecycle data for {lifecycle_doc_id}")
                        logger.info(f"Data stored: {lifecycle_data}")
                    except Exception as e:
                        logger.warning(f"Could not store trade lifecycle data for {lifecycle_doc_id}: {e}")
                    # --- End fx_lifecycle storage ---
                
                # Store in appropriate repository based on trade type
                if is_forex_trade:
                    # Try to create Forex model and save
                    try:
                        forex = Forex(**{k.replace(' ', ''): v for k, v in row.items()})
                        forex_repository.save_forex(forex)
                    except Exception as e:
                        logger.warning(f"Could not save forex trade {trade_id}: {e}")
                else:
                    # Try to create Trade model and save
                    try:
                        trade = Trade(**{k.replace(' ', '_'): v for k, v in row.items()})
                        trade_repository.save_trade(trade)
                    except Exception as e:
                        logger.warning(f"Could not save equity trade {trade_id}: {e}")
    
        # Always overwrite Maturity_Forex.csv for testing
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info(f"Overwriting filtered_trades/Maturity_Forex.csv with uploaded file: {file.filename}")
        df.to_csv('filtered_trades/Maturity_Forex.csv', index=False)

        files = []
        for filename in os.listdir("filtered_trades"):
            if filename.endswith(".csv") and not filename.startswith("maturity_download_") and not filename.startswith("coupon_download_"):
                files.append({
                    'filename': filename,
                    'download_url': f"/filtered_trades/{filename}"
                })
        return templates.TemplateResponse("overview.html", {
            "request": request,
            "files": files,
            "events": EVENTS,
            "success_message": f"File processed and trades sorted successfully!"
        })
    except Exception as e:
        files = []
        for filename in os.listdir("filtered_trades"):
            if filename.endswith(".csv") and not filename.startswith("maturity_download_") and not filename.startswith("coupon_download_"):
                files.append({
                    'filename': filename,
                    'download_url': f"/filtered_trades/{filename}"
                })
        return templates.TemplateResponse("overview.html", {
            "request": request,
            "files": files,
            "events": EVENTS,
            "error_message": f"Error processing file: {str(e)}"
        })

@router.get("/event/maturity-forex", response_class=HTMLResponse)
def maturity_forex_page(request: Request):
    from .routes import EVENTS  # Ensure EVENTS is imported if needed
    return templates.TemplateResponse("maturity_forex.html", {"request": request, "events": EVENTS, "event_type": "maturity-forex"})

@router.get("/event/{event_type}", response_class=HTMLResponse)
def event_page(request: Request, event_type: str):
    valid_types = [e[0] for e in EVENTS]
    if event_type not in valid_types:
        return HTMLResponse("Invalid event type", status_code=404)
    is_maturity = event_type == "Maturity"
    is_coupon = event_type == "Coupon Rate"
    return templates.TemplateResponse("event_page.html", {
        "request": request,
        "event_type": event_type,
        "event_label": dict(EVENTS)[event_type],
        "events": EVENTS,
        "is_maturity": is_maturity,
        "is_coupon": is_coupon
    })

def get_filtered_trades(event_type):
    possible_filenames = [
        f"filtered_trades/{event_type}.csv",
        f"filtered_trades/{event_type.replace(' ', '_')}.csv",
        f"filtered_trades/{event_type.replace(' ', '-')}.csv",
        f"filtered_trades/{event_type.replace('-', '_')}.csv",
        f"filtered_trades/{event_type.replace('_', '-')}.csv",
    ]
    filename = None
    for fname in possible_filenames:
        if os.path.exists(fname):
            filename = fname
            break
    if not filename:
        logger.debug(f"Debug: Could not find file for event_type '{event_type}'. Tried: {possible_filenames}")
        return []
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    # Strip whitespace from all string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    return df.to_dict(orient="records")

@router.get("/api/event/{event_type}")
def api_event_trades(event_type: str):
    logger.info(f"Debug: API called with event_type: '{event_type}'")
    normalized_event_type = event_type.lower()

    # Handle maturity-forex specifically
    if normalized_event_type == "maturity-forex":
        # Get data directly from fx_capture Firestore collection
        try:
            db = get_firestore_client()
            logger.info(f"Debug: Firestore client created successfully")
            
            # Test if we can access any collection
            collections = list(db.collections())
            logger.info(f"Debug: Available collections: {[col.id for col in collections]}")
            
            # Check if fx_capture collection exists
            fx_capture_ref = db.collection("fx_capture")
            logger.info(f"Debug: fx_capture collection reference created")
            
            # Get all documents from fx_capture collection (like validation service)
            docs = list(fx_capture_ref.stream())
            logger.info(f"Debug: Retrieved {len(docs)} documents from fx_capture")
            
            trades = [doc.to_dict() for doc in docs]
            logger.info(f"Debug: Total trades in fx_capture: {len(trades)}")
            
            # Show first few trade IDs for debugging
            if trades:
                first_trade = trades[0]
                logger.info(f"Debug: First trade keys: {list(first_trade.keys())}")
                logger.info(f"Debug: First trade TradeID: {first_trade.get('TradeID', 'NOT_FOUND')}")
                logger.info(f"Debug: First trade ID field: {first_trade.get('id', 'NOT_FOUND')}")
            else:
                logger.info(f"Debug: No trades found in fx_capture collection")
            
            # Filter for FX trades (be more flexible with field names)
            fx_trades = []
            for trade in trades:
                trade_id = trade.get('TradeID', trade.get('trade_id', trade.get('id', '')))
                if str(trade_id).upper().startswith('FX'):
                    fx_trades.append(trade)
            
            logger.info(f"Debug: Found {len(fx_trades)} FX trades from fx_capture collection")
            logger.info(f"Debug: Returning {len(fx_trades)} FX trades (no validation filtering)")
            
            cleaned_trades = clean_for_json(fx_trades)
            return JSONResponse(cleaned_trades)
            
        except Exception as e:
            logger.error(f"Debug: Error in maturity-forex endpoint: {e}")
            import traceback
            logger.error(f"Debug: Full traceback: {traceback.format_exc()}")
            return JSONResponse([])
    
    # Normal handling for other event types
    if normalized_event_type in ["maturity", "coupon rate", "early-redemption"]:
        # Get data directly from fx_capture Firestore collection for all forex events
        db = get_firestore_client()
        logger.info(f"Debug: Fetching data from fx_capture collection for {event_type}")
        
        try:
            # Get all documents from fx_capture collection (like validation service)
            trades = [doc.to_dict() for doc in db.collection("fx_capture").stream()]
            logger.info(f"Debug: Total trades in fx_capture for {event_type}: {len(trades)}")
            
            # Filter for FX trades (be more flexible with field names)
            fx_trades = []
            for trade in trades:
                trade_id = trade.get('TradeID', trade.get('trade_id', trade.get('id', '')))
                if str(trade_id).upper().startswith('FX'):
                    fx_trades.append(trade)
            
            logger.info(f"Debug: Found {len(fx_trades)} FX trades from fx_capture collection")
            logger.info(f"Debug: Returning {len(fx_trades)} FX trades for {event_type}")
            
            cleaned_trades = clean_for_json(fx_trades)
            return JSONResponse(cleaned_trades)
            
        except Exception as e:
            logger.error(f"Debug: Error fetching from fx_capture: {e}")
            return JSONResponse([])
    else:
        logger.info(f"Debug: Using get_filtered_trades() for '{event_type}'")
        trades = get_filtered_trades(event_type)
        logger.info(f"Debug: Returning {len(trades)} trades")
        cleaned_trades = clean_for_json(trades)
        return JSONResponse(cleaned_trades)

@router.post("/api/event/maturity/approve/{trade_id}")
def api_approve_maturity(trade_id: str):
    approve_maturity_trade(trade_id)
    # Log to fx_lifecycle only for Forex trades
    if trade_id.upper().startswith('FX'):
        firestore_db = get_firestore_client()
        log_data = {
            'trade_id': trade_id,
            'event_type': 'Maturity',
            'action': 'approve',
            'timestamp': datetime.utcnow().isoformat(),
        }
        try:
            firestore_db.collection('fx_lifecycle').document(str(uuid.uuid4())).set(log_data)
        except Exception as e:
            logger.warning(f"Could not log maturity approval for {trade_id}: {e}")
    return JSONResponse({"status": "approved"})

@router.post("/api/event/coupon/approve/{trade_id}")
def api_approve_coupon(trade_id: str):
    approve_coupon_trade(trade_id)
    # Log to fx_lifecycle only for Forex trades
    if trade_id.upper().startswith('FX'):
        firestore_db = get_firestore_client()
        log_data = {
            'trade_id': trade_id,
            'event_type': 'Coupon Rate',
            'action': 'approve',
            'timestamp': datetime.utcnow().isoformat(),
        }
        try:
            firestore_db.collection('fx_lifecycle').document(str(uuid.uuid4())).set(log_data)
        except Exception as e:
            logger.warning(f"Could not log coupon approval for {trade_id}: {e}")
    return JSONResponse({"status": "approved"})

@router.post("/api/event/coupon/pay/{trade_id}")
def api_pay_coupon(trade_id: str):
    success = pay_coupon(trade_id)
    # Log to fx_lifecycle only for Forex trades
    if trade_id.upper().startswith('FX'):
        firestore_db = get_firestore_client()
        log_data = {
            'trade_id': trade_id,
            'event_type': 'Coupon Rate',
            'action': 'pay_coupon',
            'timestamp': datetime.utcnow().isoformat(),
            'success': success,
        }
        try:
            firestore_db.collection('fx_lifecycle').document(str(uuid.uuid4())).set(log_data)
        except Exception as e:
            logger.warning(f"Could not log coupon payment for {trade_id}: {e}")
    if success:
        return JSONResponse({"status": "coupon paid"})
    else:
        return JSONResponse({"error": "Coupon payment failed or not due"}, status_code=400)


@router.post("/api/event/approve")
async def approve_trade(request: Request):
    data = await request.json()
    trade_id = data.get("TradeID")
    trade_type = data.get("TradeType")  # 'Equity' or 'Forex'
    if not trade_id or not trade_type:
        return JSONResponse({"error": "Missing TradeID or TradeType"}, status_code=400)

    if trade_type == "Equity":
        json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../equity_capture/db/trades.json'))
    else:
        json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../forex_capture/db/forex.json'))

    # Load, update, and save
    with open(json_path, "r") as f:
        trades = json.load(f)
    updated = False
    for t in trades:
        if str(t.get("TradeID")) == str(trade_id):
            t["ApprovalStatus"] = "Approved"
            updated = True
            break
    if updated:
        with open(json_path, "w") as f:
            json.dump(trades, f, indent=2)
        return JSONResponse({"status": "ok"})
    else:
        return JSONResponse({"error": "Trade not found"}, status_code=404)

@router.get("/api/event/early-redemption")
def api_early_redemption_trades():
    trades = get_early_redemption_trades()
    return JSONResponse(trades)

@router.get("/api/event/early-redemption/trade/{trade_id}")
def api_early_redemption_trade(trade_id: str):
    trade = get_early_redemption_trade(trade_id)
    if trade:
        return JSONResponse(trade)
    return JSONResponse({"error": "Trade not found"}, status_code=404)

@router.post("/api/event/early-redemption/redeem/{trade_id}")
async def api_redeem_early_redemption(trade_id: str, request: Request):
    data = await request.json()
    entered_price = data.get('entered_price') if isinstance(data, dict) else None
    trades = get_early_redemption_trades()
    for trade in trades:
        if str(trade.get('Trade ID', '')) == str(trade_id):
            trade_date = trade.get('Trade Date', None)
            obs_months = trade.get('Observation Dates', None)
            if trade_date and obs_months is not None:
                try:
                    obs_months = int(obs_months)
                except (ValueError, TypeError):
                    return JSONResponse({'error': 'Invalid observation months'}, status_code=400)
                trade_date_obj = parse_date(trade_date)
                if not trade_date_obj:
                    return JSONResponse({'error': 'Invalid trade date'}, status_code=400)
                today = datetime.now().date()
                mark_trade_redeemed(trade_id, trade_date_obj, obs_months, today, entered_price)
                # Log to fx_lifecycle only for Forex trades
                if trade_id.upper().startswith('FX'):
                    firestore_db = get_firestore_client()
                    log_data = {
                        'trade_id': trade_id,
                        'event_type': 'Early-Redemption',
                        'action': 'redeem',
                        'timestamp': datetime.utcnow().isoformat(),
                        'entered_price': entered_price,
                    }
                    try:
                        firestore_db.collection('fx_lifecycle').document(str(uuid.uuid4())).set(log_data)
                    except Exception as e:
                        logger.warning(f"Could not log early redemption for {trade_id}: {e}")
                return JSONResponse({'status': 'redeemed'})
    return JSONResponse({'error': 'Trade not found'}, status_code=404)

@router.get("/download/Early-Redemption")
def download_early_redemption_file():
    trades = get_early_redemption_trades()
    if not trades:
        return HTMLResponse("No early redemption trades found", status_code=404)
    df = pd.DataFrame(trades)
    temp_filename = f"filtered_trades/early_redemption_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(temp_filename, index=False)
    return FileResponse(temp_filename, filename=f"early_redemption_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

@router.get("/download/{event_type}")
def download_event_file(event_type: str):
    if event_type == "Maturity":
        trades = get_maturity_trades()
        if not trades:
            return HTMLResponse("No maturity trades found", status_code=404)
        df = pd.DataFrame(trades)
        columns_to_exclude = ['Maturity Reached', 'Number of days']
        df = df.drop(columns=[col for col in df.columns if col in columns_to_exclude])
        temp_filename = f"filtered_trades/maturity_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(temp_filename, index=False)
        return FileResponse(temp_filename, filename=f"maturity_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    elif event_type == "Coupon Rate":
        trades = get_coupon_trades()
        if not trades:
            return HTMLResponse("No coupon trades found", status_code=404)
        df = pd.DataFrame(trades)
        temp_filename = f"filtered_trades/coupon_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(temp_filename, index=False)
        return FileResponse(temp_filename, filename=f"coupon_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    else:
        possible_filenames = [
            f"filtered_trades/{event_type}.csv",
            f"filtered_trades/{event_type.replace(' ', '_')}.csv",
            f"filtered_trades/{event_type.replace(' ', '-')}.csv",
            f"filtered_trades/{event_type.replace('-', '_')}.csv",
            f"filtered_trades/{event_type.replace('_', '-')}.csv",
        ]
        filename = None
        for fname in possible_filenames:
            if os.path.exists(fname):
                filename = fname
                break
        if not filename:
            return HTMLResponse("File not found", status_code=404)
        return FileResponse(filename, filename=os.path.basename(filename))

@router.get("/api/event/maturity-forex")
def api_maturity_forex_trades():
    """Fetch only necessary FX trade data from Firebase for maturity events UI table"""
    try:
        db = get_firestore_client()
        logger.info("Debug: Fetching minimal data from fx_capture collection for maturity-forex")
        
        # Query all trades and select only necessary fields
        all_trades = []
        for doc in db.collection("fx_capture").stream():
            trade_data = doc.to_dict()
            trade_id = trade_data.get('TradeID', trade_data.get('trade_id', trade_data.get('id', '')))
            
            # Extract only the fields needed for UI table - using frontend-expected field names
            ui_trade = {
                "TradeID": trade_id,
                "Symbol": trade_data.get('CurrencyPair', ''),
                "CurrencyPair": trade_data.get('CurrencyPair', ''),
                "EventType": "Maturity",
                "event_type": "Maturity",
                "EventDate": trade_data.get('MaturityDate', trade_data.get('SettlementDate', '')),
                "TradeDate": trade_data.get('TradeDate', ''),
                "Instrument": "Forex"  # Add Instrument field for frontend filtering
            }
            all_trades.append(ui_trade)
        
        logger.info(f"Debug: Found {len(all_trades)} trades for maturity-forex UI table")
        logger.info(f"Debug: Returning minimal data for {len(all_trades)} trades")
        
        return JSONResponse(all_trades)
        
    except Exception as e:
        logger.error(f"Debug: Error fetching from fx_capture: {e}")
        import traceback
        logger.error(f"Debug: Full traceback: {traceback.format_exc()}")
        return JSONResponse([])

@router.get("/api/event/maturity-forex/trade/{trade_id}")
def api_maturity_forex_trade(trade_id: str):
    logger.info("!!! INSIDE MATURITY FOREX TRADE ENDPOINT !!!")
    filename = "filtered_trades/Maturity_Forex.csv"
    logger.info(f"Looking for trade {trade_id} in {filename}")
    if not os.path.exists(filename):
        logger.error(f"File {filename} not found!")
        return JSONResponse({"error": "Trade not found"}, status_code=404)
    
    # Load and clean data
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    df = df.replace([np.inf, -np.inf], np.nan).fillna('')
    
    # Clean trade IDs in DataFrame and search parameter
    df['TradeID'] = df['TradeID'].astype(str).str.strip()
    trade_id = str(trade_id).strip()
    
    # Debug logging
    logger.info(f"First few TradeIDs in CSV: {df['TradeID'].head(5).tolist()}")
    logger.info(f"Looking for trade_id: '{trade_id}'")
    logger.info(f"Column names in CSV: {df.columns.tolist()}")
    
    # Case-insensitive comparison
    trade = df[df['TradeID'].str.upper() == trade_id.upper()]
    logger.info(f"Found trade? {not trade.empty}")
    
    if trade.empty:
        return JSONResponse({"error": "Trade not found"}, status_code=404)
    
    # Clean and return the trade data
    trade_dict = trade.iloc[0].to_dict()
    cleaned_trade = clean_for_json(trade_dict)
    return JSONResponse(cleaned_trade)

# Removed duplicate router and endpoint definitions


@router.post("/api/event/maturity-forex/approve/{trade_id}")
def approve_maturity_forex_trade(trade_id: str):
    # This function needs to be updated to use a repository for approvals
    # For now, it will just return a placeholder response
    return JSONResponse({"status": "approved (placeholder)"})

@router.get("/api/event/maturity-forex/approved/{trade_id}")
def is_maturity_forex_trade_approved(trade_id: str):
    # This function needs to be updated to use a repository for approvals
    # For now, it will just return a placeholder response
    return JSONResponse({"approved": False}) # Placeholder

@router.get("/api/event/maturity-forex/download-json")
def download_maturity_forex_json():
    filename = "filtered_trades/Maturity_Forex.csv"
    if not os.path.exists(filename):
        return JSONResponse([])
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    df['TradeID'] = df['TradeID'].astype(str).str.strip()
    # Load approvals
    # This function needs to be updated to use a repository for approvals
    # For now, it will just return an empty list
    approvals = [] # Placeholder
    approvals_clean = {tid.strip().upper() for tid in approvals}
    # Calculate final amount for each trade
    def calc_final_amount(row):
        try:
            currency_pair = row.get('CurrencyPair', '')
            dealt_currency = row.get('DealtCurrency', row.get('Dealt Currency', ''))
            base_currency = row.get('BaseCurrency', row.get('Base Currency', ''))
            term_currency = row.get('TermCurrency', row.get('Term Currency', ''))
            notional_amount = float(row.get('NotionalAmount', row.get('Notional Amount', 0)))
            fx_rate = float(row.get('FXRate', row.get('FX Rate', 0)))
            if dealt_currency == base_currency:
                if base_currency == currency_pair.split('/')[0]:
                    other_amount = notional_amount * fx_rate
                    other_currency = term_currency
                else:
                    return 'Base/currency pair mismatch'
            elif dealt_currency == term_currency:
                if term_currency == currency_pair.split('/')[1]:
                    other_amount = notional_amount / fx_rate
                    other_currency = base_currency
                else:
                    return 'Term/currency pair mismatch'
            else:
                return 'Dealt currency must be base or term'
            if isinstance(other_amount, float):
                return f"{other_amount:,.2f} {other_currency}"
            else:
                return str(other_amount)
        except Exception as e:
            return 'N/A'
    trades = []
    for row in df.to_dict(orient='records'):
        trade_id_clean = str(row.get('TradeID', '')).strip().upper()
        row['FinalAmount'] = calc_final_amount(row)
        row['Approved'] = trade_id_clean in approvals_clean # Placeholder
        trades.append(row)
    # Write to a temp file and return as download
    import tempfile, json
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w', encoding='utf-8') as tmpf:
        json.dump(trades, tmpf, indent=2)
        tmpf.flush()
        tmpf_name = tmpf.name
    from fastapi.responses import FileResponse
    return FileResponse(tmpf_name, filename='maturity_forex_trades.json', media_type='application/json')

@router.get("/api/event/maturity-forex/download-csv")
def download_maturity_forex_csv():
    filename = "filtered_trades/Maturity_Forex.csv"
    if not os.path.exists(filename):
        return JSONResponse([])
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    df['TradeID'] = df['TradeID'].astype(str).str.strip()
    # Load approvals
    # This function needs to be updated to use a repository for approvals
    # For now, it will just return an empty set
    approvals = set() # Placeholder
    approvals_clean = {tid.strip().upper() for tid in approvals}
    # Calculate final amount for each trade
    def calc_final_amount(row):
        try:
            currency_pair = row.get('CurrencyPair', '')
            dealt_currency = row.get('DealtCurrency', row.get('Dealt Currency', ''))
            base_currency = row.get('BaseCurrency', row.get('Base Currency', ''))
            term_currency = row.get('TermCurrency', row.get('Term Currency', ''))
            notional_amount = float(row.get('NotionalAmount', row.get('Notional Amount', 0)))
            fx_rate = float(row.get('FXRate', row.get('FX Rate', 0)))
            if dealt_currency == base_currency:
                if base_currency == currency_pair.split('/')[0]:
                    other_amount = notional_amount * fx_rate
                    other_currency = term_currency
                else:
                    return 'Base/currency pair mismatch'
            elif dealt_currency == term_currency:
                if term_currency == currency_pair.split('/')[1]:
                    other_amount = notional_amount / fx_rate
                    other_currency = base_currency
                else:
                    return 'Term/currency pair mismatch'
            else:
                return 'Dealt currency must be base or term'
            if isinstance(other_amount, float):
                return f"{other_amount:,.2f} {other_currency}"
            else:
                return str(other_amount)
        except Exception as e:
            return 'N/A'
    trades = []
    for row in df.to_dict(orient='records'):
        trade_id_clean = str(row.get('TradeID', '')).strip().upper()
        row['FinalAmount'] = calc_final_amount(row)
        row['Approved'] = trade_id_clean in approvals_clean # Placeholder
        trades.append(row)
    # Write to a temp file and return as download
    import tempfile
    df_out = pd.DataFrame(trades)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', encoding='utf-8', newline='') as tmpf:
        df_out.to_csv(tmpf, index=False)
        tmpf.flush()
        tmpf_name = tmpf.name
    from fastapi.responses import FileResponse
    return FileResponse(tmpf_name, filename='maturity_forex_trades.csv', media_type='text/csv')

@router.get("/api/reconciliation/equity")
def get_equity_reconciliation():
    # Paths
    validation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../equity_trade_validation/db/validated_trades.json'))
    termsheet_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../equity_termsheet_capture/db/termsheets.json'))
    captured_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../equity_capture/db/trades.json'))
    rules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../equity_reconciliation/core/reconciliation_rules.json'))

    # Load data
    with open(validation_path) as f:
        validations = json.load(f)
    with open(termsheet_path) as f:
        termsheets = {str(t['TradeID']): t for t in json.load(f)}
    with open(captured_path) as f:
        captured = {str(t['TradeID']): t for t in json.load(f)}
    with open(rules_path) as f:
        rules = json.load(f)

    # Filter failed trades
    failed = [v for v in validations if v.get('status') == 'Failed']

    # Build reconciliation records
    recs = []
    for v in failed:
        tid = str(v['TradeID'])
        internal = termsheets.get(tid, {})
        external = captured.get(tid, {})
        for reason in v.get('reasons', []):
            # Extract field name from reason, e.g., 'Mismatch in Price' -> 'Price'
            field = reason.replace('Mismatch in ', '').strip()
            team = rules.get(field, '-')
            recs.append({
                'TradeID': tid,
                'InternalValue': internal.get(field, '-'),
                'ExternalValue': external.get(field, '-'),
                'ReportedTo': team,
                'Reason': reason,
                'Actions': '<button>Investigate</button>'
            })
    return JSONResponse(recs)

@router.get("/api/consolidated-data")
def get_consolidated_data():
    db = get_firestore_client()
    fx_trades = list(db.collection('fx_capture').stream())
    fx_termsheets = list(db.collection('fx_termsheets').stream())
    nwm_management = list(db.collection('NWM_Management').stream())

    # Convert docs to dicts
    fx_trades = [doc.to_dict() for doc in fx_trades]
    fx_termsheets = [doc.to_dict() for doc in fx_termsheets]
    nwm_management = [doc.to_dict() for doc in nwm_management]

    # Collate data (simple merge for now, can be improved)
    consolidated = []
    for trade in fx_trades:
        row = {
            "Trade ID": trade.get("TradeID"),
            "Trader ID": trade.get("TraderID"),
            "Currency": trade.get("CurrencyPair"),
            "Trade Date": trade.get("TradeDate"),
            "KYC Status": trade.get("KYCCheck"),
            "Validation Status": trade.get("ValidationStatus"),
            "BuySell": trade.get("BuySell"),
            "NotionalAmount": trade.get("NotionalAmount"),
            "FXRate": trade.get("FXRate"),
            "SettlementDate": trade.get("SettlementDate"),
            "Approval Status": trade.get("ApprovalStatus"),
            "INTERNAL VALUE": trade.get("InternalValue"),
            "EXTERNAL VALUE": trade.get("ExternalValue"),
            "REPORTEDTO": trade.get("ReportedTo"),
            "REASON": trade.get("Reason"),
        }
        consolidated.append(row)
    # Add NWM_Management data (add missing columns as None)
    for item in nwm_management:
        row = {col: item.get(col.replace(" ", ""), None) for col in CONSOLIDATED_COLUMNS}
        consolidated.append(row)
    return JSONResponse(consolidated)



@router.post("/api/consolidated-data/upload")
def upload_consolidated_data(data: list):
    db = get_firestore_client()
    for row in data:
        trade_id = row.get("Trade ID")
        if trade_id:
            db.collection("middle_office").document(str(trade_id)).set(row)
    return {"status": "success", "count": len(data)}
