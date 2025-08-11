import os
import json
from datetime import datetime, timedelta
import pandas as pd
import math

APPROVALS_FILE = 'coupon_approvals.json'
PAYMENTS_FILE = 'coupon_payments.json'

# Load or initialize approvals
if os.path.exists(APPROVALS_FILE):
    with open(APPROVALS_FILE, 'r') as f:
        coupon_approvals = json.load(f)
else:
    coupon_approvals = {}

# Load or initialize payments
if os.path.exists(PAYMENTS_FILE):
    with open(PAYMENTS_FILE, 'r') as f:
        coupon_payments = json.load(f)
else:
    coupon_payments = {}

def save_approvals():
    with open(APPROVALS_FILE, 'w') as f:
        json.dump(coupon_approvals, f, indent=2)

def save_payments():
    with open(PAYMENTS_FILE, 'w') as f:
        json.dump(coupon_payments, f, indent=2)

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

def parse_date(date_str):
    """Parse date string in various formats"""
    if not date_str or str(date_str).lower() == 'nan':
        return None
    
    date_str = str(date_str).strip()
    
    # Try YYYY-DD-MM format first (as seen in the data: 2025-23-07)
    if date_str.count('-') == 2:
        try:
            parts = date_str.split('-')
            if len(parts) == 3:
                yyyy = int(parts[0])
                dd = int(parts[1])
                mm = int(parts[2])
                # Check if this is YYYY-DD-MM format (day > 12)
                if dd > 12 and mm <= 12:
                    return datetime(yyyy, mm, dd).date()
        except (ValueError, TypeError):
            pass
    
    # Try standard formats
    formats = ['%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y', '%Y/%m/%d', '%d/%m/%Y']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None

def calculate_coupon_due_dates(trade_date, coupon_schedule):
    """Calculate when coupon payments are due based on schedule"""
    if not trade_date or not coupon_schedule or str(coupon_schedule).lower() == 'nan':
        return []
    
    trade_date_obj = parse_date(trade_date)
    if not trade_date_obj:
        return []
    
    schedule_lower = str(coupon_schedule).strip().lower()
    due_dates = []
    
    if 'annual' in schedule_lower:
        # Annual payments - every 365 days from trade date
        current_date = trade_date_obj
        for i in range(1, 6):  # Calculate next 5 years of payments
            due_date = current_date + timedelta(days=365)
            due_dates.append(due_date)
            current_date = due_date
    elif 'semi-annual' in schedule_lower or 'semi annual' in schedule_lower:
        # Semi-annual payments - every 183 days from trade date
        current_date = trade_date_obj
        for i in range(1, 11):  # Calculate next 5 years of payments (10 semi-annual payments)
            due_date = current_date + timedelta(days=183)
            due_dates.append(due_date)
            current_date = due_date
    elif 'quarterly' in schedule_lower:
        # Quarterly payments - every 91.25 days from trade date
        current_date = trade_date_obj
        for i in range(1, 21):  # Calculate next 5 years of payments (20 quarterly payments)
            due_date = current_date + timedelta(days=91.25)
            due_dates.append(due_date)
            current_date = due_date
    
    return due_dates

def is_coupon_due(trade_id, trade_date, coupon_schedule):
    """Check if a coupon payment is currently due and within the allowed time window"""
    if not trade_id or not trade_date or not coupon_schedule or str(coupon_schedule).lower() == 'nan':
        return False
    
    trade_date_obj = parse_date(trade_date)
    if not trade_date_obj:
        return False
    
    today = datetime.now().date()
    
    # Calculate the time limit based on schedule
    schedule_lower = str(coupon_schedule).strip().lower()
    if 'annual' in schedule_lower:
        time_limit_days = 365
    elif 'semi-annual' in schedule_lower or 'semi annual' in schedule_lower:
        time_limit_days = 183
    elif 'quarterly' in schedule_lower:
        time_limit_days = 91
    else:
        # Default to annual if schedule is not recognized
        time_limit_days = 365
    
    # Check if we're within the time limit from trade date
    days_since_trade = (today - trade_date_obj).days
    if days_since_trade > time_limit_days:
        return False  # Too much time has passed
    
    due_dates = calculate_coupon_due_dates(trade_date, coupon_schedule)
    
    # Check if any due date is within the last 30 days (payment window)
    for due_date in due_dates:
        if due_date <= today <= due_date + timedelta(days=30):
            # Check if this payment hasn't been made yet
            payment_key = f"{trade_id}_{due_date.strftime('%Y-%m-%d')}"
            if payment_key not in coupon_payments:
                return True
    
    return False

def get_coupon_trades():
    filenames = ['filtered_trades/Coupon_Rate.csv', 'filtered_trades/Coupon Rate.csv']
    filename = None
    for fname in filenames:
        if os.path.exists(fname):
            filename = fname
            break
    if not filename:
        return []
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    trades = []
    for trade in df.to_dict(orient='records'):
        trade_id = str(trade.get('Trade ID', ''))
        # Get coupon rate (handle case sensitivity and whitespace)
        coupon_rate = None
        for col in df.columns:
            if col.strip().lower() in ['coupon rate', 'couponrate', 'coupon_rate']:
                coupon_rate = trade.get(col, None)
                break
        # Get coupon schedule (handle case sensitivity and whitespace)
        coupon_schedule = None
        for col in df.columns:
            if col.strip().lower() in ['coupon schedule', 'couponschedule', 'coupon_schedule', 'schedule']:
                coupon_schedule = trade.get(col, None)
                break
        # Get trade date
        trade_date = trade.get('Trade Date', '')
        # Get trade value safely
        trade_value = safe_float(trade.get('Trade Value', 0))
        if trade_value is None:
            trade_value = 0
        # Calculate coupon payment amount (simplified calculation)
        coupon_payment = 0
        if coupon_rate and trade_value and trade_value > 0:
            try:
                rate = safe_float(str(coupon_rate).replace('%', '').strip())
                if rate is not None and rate > 0:
                    coupon_payment = (rate / 100) * trade_value
                    if math.isnan(coupon_payment) or math.isinf(coupon_payment):
                        coupon_payment = 0
            except (ValueError, TypeError):
                coupon_payment = 0
        approved = coupon_approvals.get(trade_id, False)
        # Calculate coupon due dates and check if payment is due
        due_dates = calculate_coupon_due_dates(trade_date, coupon_schedule)
        is_due = is_coupon_due(trade_id, trade_date, coupon_schedule)
        # Get next due date
        next_due_date = None
        today = datetime.now().date()
        for due_date in due_dates:
            if due_date > today:
                next_due_date = due_date
                break
        # Get the last payment date for this trade
        last_payment_date = None
        for payment_key, payment_data in coupon_payments.items():
            if payment_data.get('trade_id') == trade_id:
                payment_date = payment_data.get('paid_date')
                if payment_date:
                    if last_payment_date is None or payment_date > last_payment_date:
                        last_payment_date = payment_date
        trades.append({
            **trade,
            'Coupon Rate': coupon_rate if coupon_rate is not None else 'N/A',
            'Coupon Schedule': coupon_schedule if coupon_schedule is not None else 'N/A',
            'Trade Date': trade_date,
            'Trade Value': trade_value,
            'Coupon Payment': coupon_payment,
            'Coupon Paid': last_payment_date if last_payment_date else 'Not Paid',
            'Coupon Due': is_due,
            'Next Due Date': next_due_date.strftime('%Y-%m-%d') if next_due_date else 'N/A',
            'Payment Status': 'Due' if is_due else 'Not Due'
        })
    return trades

def approve_coupon_trade(trade_id):
    coupon_approvals[trade_id] = True
    save_approvals()
    return True

def pay_coupon(trade_id):
    """Pay a coupon for a specific trade"""
    # Find the trade to get its details
    trades = get_coupon_trades()
    target_trade = None
    
    for trade in trades:
        if str(trade.get('Trade ID', '')) == trade_id:
            target_trade = trade
            break
    
    if not target_trade:
        return False
    
    trade_date = target_trade.get('Trade Date', '')
    coupon_schedule = target_trade.get('Coupon Schedule', '')
    
    # Calculate due dates and find the one that's currently due
    due_dates = calculate_coupon_due_dates(trade_date, coupon_schedule)
    today = datetime.now().date()
    
    for due_date in due_dates:
        if due_date <= today <= due_date + timedelta(days=30):
            # This payment is due, mark it as paid
            payment_key = f"{trade_id}_{due_date.strftime('%Y-%m-%d')}"
            coupon_payments[payment_key] = {
                'trade_id': trade_id,
                'due_date': due_date.strftime('%Y-%m-%d'),
                'paid_date': today.strftime('%Y-%m-%d'),
                'amount': target_trade.get('Coupon Payment', 0)
            }
            save_payments()
            return True
    
    return False 