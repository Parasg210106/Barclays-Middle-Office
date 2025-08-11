import os
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json

REDEEMED_FILE = 'redeemed_status.json'

def parse_date(date_str):
    """Parse date string in various formats"""
    if not date_str or str(date_str).strip() == '':
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
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y', '%Y/%m/%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except Exception:
            continue
    return None

def load_redeemed_status():
    if os.path.exists(REDEEMED_FILE):
        with open(REDEEMED_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_redeemed_status(status):
    with open(REDEEMED_FILE, 'w') as f:
        json.dump(status, f)

def mark_trade_redeemed(trade_id, trade_date, obs_months, today, entered_price):
    # Calculate the period in months for this redemption
    year_diff = today.year - trade_date.year
    month_diff = today.month - trade_date.month
    total_months = year_diff * 12 + month_diff
    if obs_months > 0 and total_months >= obs_months:
        periods = total_months // obs_months
        period_months = periods * obs_months
        key = f"{trade_id}|{period_months}"
        status = load_redeemed_status()
        status[key] = {
            'redeemed': True,
            'last_redeemed_date': today.isoformat(),
            'entered_price': entered_price
        }
        save_redeemed_status(status)

def get_early_redemption_trades():
    filename = 'filtered_trades/Early-Redemption.csv'
    if not os.path.exists(filename):
        return []
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    trades = []
    today = datetime.now().date()
    redeemed_status = load_redeemed_status()
    for trade in df.to_dict(orient='records'):
        trade_date = parse_date(trade.get('Trade Date', ''))
        obs_months = trade.get('Observation Dates', None)
        try:
            obs_months = int(obs_months)
        except (ValueError, TypeError):
            obs_months = None
        check_accessible = False
        redeemed = False
        period_months = None
        last_redeemed_date = None
        entered_price = None
        coupon_rate = trade.get('Coupon rate', '')
        coupon_schedule = trade.get('Coupon schedule', '')
        if trade_date and obs_months is not None and obs_months > 0:
            year_diff = today.year - trade_date.year
            month_diff = today.month - trade_date.month
            total_months = year_diff * 12 + month_diff
            if total_months >= obs_months:
                periods = total_months // obs_months
                period_months = periods * obs_months
                period_date = trade_date + relativedelta(months=period_months)
                if today == period_date:
                    key = f"{trade.get('Trade ID','')}|{period_months}"
                    redeemed_info = redeemed_status.get(key, {})
                    redeemed = redeemed_info.get('redeemed', False) if isinstance(redeemed_info, dict) else redeemed_info
                    last_redeemed_date = redeemed_info.get('last_redeemed_date') if isinstance(redeemed_info, dict) else None
                    entered_price = redeemed_info.get('entered_price') if isinstance(redeemed_info, dict) else None
                    if not redeemed:
                        check_accessible = True
        trades.append({
            **trade,
            'Check Accessible': check_accessible,
            'Redeemed': redeemed,
            'Last Redeemed Date': last_redeemed_date,
            'Entered Price': entered_price,
            'Coupon Rate': coupon_rate,
            'Coupon Schedule': coupon_schedule
        })
    return trades

def calculate_months_difference(start_date, end_date):
    """Calculate the number of months between two dates using calendar months"""
    year_diff = end_date.year - start_date.year
    month_diff = end_date.month - start_date.month
    day_diff = end_date.day - start_date.day
    
    # Calculate total months
    total_months = year_diff * 12 + month_diff
    
    # Adjust for day of month
    if day_diff < 0:
        # If the day of end_date is before the day of start_date, subtract one month
        total_months -= 1
    
    return total_months

def get_early_redemption_trade(trade_id):
    trades = get_early_redemption_trades()
    for trade in trades:
        if str(trade.get('Trade ID', '')) == str(trade_id):
            return trade
    return None 