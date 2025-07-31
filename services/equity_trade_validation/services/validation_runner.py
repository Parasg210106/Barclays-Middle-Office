import os
import json
from services.equity_trade_validation.core.rules_config import rules_config
from datetime import datetime

VALIDATED_TRADES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'validated_trades.json')

def normalize_key(key):
    if not key:
        return None
    return str(key).replace(' ', '').replace('_', '').lower()

def normalize_value(val, field=None):
    if val is None:
        return None
    
    # Convert to string and strip
    if isinstance(val, (int, float)):
        val = str(val)
    elif isinstance(val, str):
        val = val.strip()
    else:
        val = str(val)
    
    # For case-insensitive fields, convert to lowercase
    if field and field.lower() in ['trade type', 'settlement status', 'kyc status', 'reference data validated']:
        val = val.lower()
    
    # Try to parse dates for date fields
    if field and 'date' in field.lower():
        # Try multiple date formats
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%m-%d-%Y", "%d-%m-%Y"):
            try:
                parsed_date = datetime.strptime(val, fmt)
                return parsed_date.strftime("%Y-%m-%d")  # Return consistent format
            except Exception:
                continue
        # If no date format matches, return original value
        return val
    
    # For numeric fields, try to normalize to same format
    if field and field.lower() in ['quantity', 'price', 'trade value', 'commission', 'taxes', 'total cost']:
        try:
            # Convert to float and back to string to normalize format
            float_val = float(val)
            return str(float_val)
        except Exception:
            return val
    
    return val

def extract_trade_id(trade):
    return trade.get('TradeID') or trade.get('Trade ID') or trade.get('trade_id')

def validate_trades(captured_trades, termsheet):
    results = []
    debug_fields = ["Trade Type", "Trade Date", "Settlement Date"]
    debug_printed = False
    
    print(f"🔍 Validation Debug: Processing {len(captured_trades)} trades against {len(termsheet)} termsheets")
    
    if captured_trades:
        print('First trade keys:', list(captured_trades[0].keys()))
        print('First trade Trade ID:', captured_trades[0].get('TradeID') or captured_trades[0].get('Trade ID'))
    
    if termsheet:
        print('First termsheet keys:', list(termsheet[0].keys()))
        print('First termsheet Trade ID:', termsheet[0].get('Trade ID') or termsheet[0].get('TradeID'))
    
    # Build termsheet lookup by normalized Trade ID
    termsheet_by_id = {}
    for t in termsheet:
        ts_id = t.get('TradeID') or t.get('Trade ID') or t.get('trade_id')
        norm_ts_id = normalize_key(ts_id)
        if norm_ts_id:
            termsheet_by_id[norm_ts_id] = t
            print(f"   Added termsheet with normalized ID: '{norm_ts_id}' (original: '{ts_id}')")
    
    print(f"   Built termsheet lookup with {len(termsheet_by_id)} entries")
    print(f"   Available normalized termsheet IDs: {list(termsheet_by_id.keys())}")
    
    for i, trade in enumerate(captured_trades):
        print(f"\n🔍 Processing trade {i+1}:")
        
        # Normalize trade fields
        norm_trade = {normalize_key(k): v for k, v in trade.items()}
        trade_id = norm_trade.get('tradeid')
        norm_trade_id = normalize_key(trade_id)
        
        print(f"   Trade ID: '{trade_id}' -> normalized: '{norm_trade_id}'")
        
        if not norm_trade_id:
            print(f"   ❌ Missing Trade ID - marking as Pending")
            results.append({'TradeID': '', 'status': 'Pending', 'reasons': ['Missing TradeID']})
            continue
        
        # Check if termsheet exists
        ts = termsheet_by_id.get(norm_trade_id)
        if not ts:
            print(f"   ❌ No matching termsheet found for Trade ID '{norm_trade_id}'")
            results.append({'TradeID': trade_id, 'status': 'Failed', 'reasons': ['No matching termsheet']})
            continue
        
        print(f"   ✅ Found matching termsheet")
        
        # Normalize termsheet fields
        norm_ts = {normalize_key(k): v for k, v in ts.items()}
        
        # Check mandatory fields
        status = 'Success'
        reasons = []
        missing_fields = []
        
        print(f"   🔍 Checking mandatory fields: {rules_config['mandatory_fields']}")
        print(f"   📋 Available trade fields: {list(norm_trade.keys())}")
        print(f"   📋 Available termsheet fields: {list(norm_ts.keys())}")
        
        for field in rules_config['mandatory_fields']:
            norm_field = normalize_key(field)
            trade_val = norm_trade.get(norm_field)
            ts_val = norm_ts.get(norm_field)
            
            print(f"      Field '{field}' (norm: '{norm_field}'): trade='{trade_val}', termsheet='{ts_val}'")
            
            if trade_val is None:
                missing_fields.append(f"Trade missing: {field}")
            if ts_val is None:
                missing_fields.append(f"Termsheet missing: {field}")
        
        if missing_fields:
            print(f"   ❌ Missing mandatory fields: {missing_fields}")
            status = 'Failed'
            reasons.extend(missing_fields)
        else:
            print(f"   ✅ All mandatory fields present")
        
        # Compare field values if termsheet exists and no missing fields
        if status == 'Success':
            mismatched_fields = []
            
            for field in rules_config['mandatory_fields']:
                norm_field = normalize_key(field)
                trade_val = norm_trade.get(norm_field)
                ts_val = norm_ts.get(norm_field)
                n_trade_val = normalize_value(trade_val, field)
                n_ts_val = normalize_value(ts_val, field)
                
                if field in debug_fields and not debug_printed:
                    print(f"   Comparing {field}: trade='{trade_val}' (norm='{n_trade_val}') vs termsheet='{ts_val}' (norm='{n_ts_val}')")
                
                if n_trade_val is not None and n_ts_val is not None and n_trade_val != n_ts_val:
                    print(f"   ❌ Mismatch in {field}: '{n_trade_val}' != '{n_ts_val}'")
                    mismatched_fields.append((field, n_trade_val, n_ts_val))
                elif n_trade_val is not None and n_ts_val is not None:
                    print(f"   ✅ Match in {field}: '{n_trade_val}' == '{n_ts_val}'")
            
            if mismatched_fields:
                print(f"   ❌ Field mismatches: {mismatched_fields}")
                status = 'Failed'
                # Generate detailed mismatch messages
                for field, trade_val, ts_val in mismatched_fields:
                    reasons.append(f'{field} mismatch: trade=\'{trade_val}\' vs termsheet=\'{ts_val}\'')
            else:
                print(f"   ✅ All field values match")
        
        print(f"   Final status: {status}, Reasons: {reasons}")
        results.append({'TradeID': trade_id, 'status': status, 'reasons': reasons})
        
        if not debug_printed:
            debug_printed = True
    
    # Summary
    success_count = sum(1 for r in results if r['status'] == 'Success')
    failed_count = sum(1 for r in results if r['status'] == 'Failed')
    pending_count = sum(1 for r in results if r['status'] == 'Pending')
    
    print(f"\n📊 Validation Summary: Success={success_count}, Failed={failed_count}, Pending={pending_count}")
    
    try:
        with open(VALIDATED_TRADES_PATH, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        print(f"Failed to save validated trades: {e}")
    
    return results
