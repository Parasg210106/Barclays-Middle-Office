import os
import json
from datetime import datetime
import pandas as pd
import math

APPROVALS_FILE = 'maturity_approvals.json'

# Load or initialize approvals
if os.path.exists(APPROVALS_FILE):
    with open(APPROVALS_FILE, 'r') as f:
        maturity_approvals = json.load(f)
else:
    maturity_approvals = {}

def save_approvals():
    with open(APPROVALS_FILE, 'w') as f:
        json.dump(maturity_approvals, f, indent=2)

def safe_float(value):
    """Convert value to float safely, handling inf/nan values"""
    if value is None:
        return None
    try:
        result = float(str(value).replace(',', ''))
        if math.isnan(result) or math.isinf(result):
            return None
        return result
    except (ValueError, TypeError):
        return None

def get_maturity_trades():
    filename = 'filtered_trades/Maturity.csv'
    if not os.path.exists(filename):
        filename = 'filtered_trades/Maturity.csv'
    if not os.path.exists(filename):
        return []
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    # Find the correct maturity date column (case/whitespace robust)
    maturity_col = None
    for col in df.columns:
        if col.strip().lower() == 'maturity date':
            maturity_col = col
            break
    if not maturity_col:
        for col in df.columns:
            if col.strip().lower() == 'settlement date':
                maturity_col = col
                break
    trades = []
    today = datetime.now().date()
    # Find the trade ID column robustly
    trade_id_col = None
    for col in df.columns:
        col_clean = col.replace(' ', '').replace('_', '').lower()
        if col_clean in ['tradeid', 'trade_id'] or ('trade' in col_clean and 'id' in col_clean):
            trade_id_col = col
            break
    if not trade_id_col:
        # fallback to first column
        trade_id_col = df.columns[0]
    for trade in df.to_dict(orient='records'):
        trade_id = str(trade.get(trade_id_col, '')).strip()
        # Exclude FX trades from equity maturity page
        if trade_id.upper().startswith('FX'):
            continue
        maturity_date_str = str(trade.get(maturity_col, '')) if maturity_col else ''
        maturity_date_str = maturity_date_str.strip()
        maturity_date = None
        if maturity_date_str:
            for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
                try:
                    maturity_date = datetime.strptime(maturity_date_str, fmt).date()
                    break
                except Exception:
                    continue
        maturity_reached = 'No'
        days_diff = '0'
        if maturity_date:
            if today >= maturity_date:
                maturity_reached = 'Yes'
                days_diff = str((today - maturity_date).days)  # days since maturity
            else:
                maturity_reached = 'No'
                days_diff = str((maturity_date - today).days)  # days to maturity
        approved = maturity_approvals.get(trade_id, False)
        # Get coupon rate (handle case sensitivity and whitespace)
        coupon_rate = None
        for col in df.columns:
            if col.strip().lower() in ['coupon rate', 'couponrate', 'coupon_rate']:
                coupon_rate = trade.get(col, None)
                break
        # Calculate final amount (Trade Value + any additional calculations)
        trade_value = safe_float(trade.get('Trade Value', 0))
        if trade_value is None:
            trade_value = 0
        # For now, final amount is the same as trade value
        final_amount = trade_value
        trades.append({
            **trade,
            'Maturity Date': maturity_date_str,
            'Maturity Reached': maturity_reached,
            'Number of days': days_diff,
            'Approved': approved,
            'Approval Status': 'Approved' if approved else 'Not Approved',
            'Coupon Rate': coupon_rate if coupon_rate is not None else 'N/A',
            'Final Amount': final_amount
        })
    return trades

def approve_maturity_trade(trade_id):
    maturity_approvals[trade_id] = True
    save_approvals()
    return True 