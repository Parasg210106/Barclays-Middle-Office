from services.equity_termsheet_capture.db.termsheet_repository import load_termsheets, save_termsheets, add_termsheet, get_termsheet_by_trade_id
import json
import os
from datetime import datetime

# Load allowed columns from equity_termsheet_rules.json and ensure 'Trade ID' is included
RULES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core', 'equity_termsheet_rules.json')
with open(RULES_PATH, 'r') as f:
    allowed_columns = list(json.load(f)["format_rules"].keys())
if "Trade ID" not in allowed_columns:
    allowed_columns = ["Trade ID"] + allowed_columns

def normalize_field_name(field_name):
    """Normalize field names to handle various formats"""
    if not field_name:
        return None
    
    # Common variations of Trade ID field
    trade_id_variations = {
        'tradeid', 'trade_id', 'trade id', 'tradeid', 'trade id',
        'TradeID', 'Trade_Id', 'Trade Id', 'Trade ID'
    }
    
    normalized = str(field_name).strip()
    if normalized.lower() in [v.lower() for v in trade_id_variations]:
        return "Trade ID"
    
    return normalized

def validate_termsheet(termsheet):
    """Validate that termsheet has required fields"""
    if not termsheet:
        return False, "Termsheet is empty"
    
    # Check for Trade ID in various formats
    trade_id_variations = ['Trade ID', 'TradeID', 'Trade_Id', 'Trade Id', 'tradeid', 'trade_id', 'trade id']
    has_trade_id = any(termsheet.get(variation) for variation in trade_id_variations)
    
    if not has_trade_id:
        return False, "Missing Trade ID field"
    
    return True, "Valid"

def normalize_date(date_str):
    """Normalize date strings to YYYY-MM-DD format"""
    if not date_str:
        return date_str
    
    date_str = str(date_str).strip()
    print(f"🔍 normalize_date input: '{date_str}'")
    
    # Try DD/MM/YYYY format (European format)
    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3:
            # Assume DD/MM/YYYY for European format
            day, month, year = parts
            try:
                result = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                print(f"🔍 normalize_date DD/MM/YYYY: '{date_str}' -> '{result}'")
                return result
            except:
                pass
    
    # Try YYYY-MM-DD format (already correct)
    if '-' in date_str and len(date_str.split('-')[0]) == 4:
        return date_str
    
    # Try MM-DD-YYYY format
    if '-' in date_str:
        parts = date_str.split('-')
        if len(parts) == 3 and len(parts[0]) <= 2:
            month, day, year = parts
            try:
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            except:
                pass
    
    return date_str

def normalize_termsheet_fields(termsheet):
    """Normalize termsheet fields to standard format"""
    normalized = {}
    
    for key, value in termsheet.items():
        if value is not None and str(value).strip() != "":
            normalized_key = normalize_field_name(key)
            if normalized_key:
                # Normalize dates
                if 'date' in normalized_key.lower():
                    normalized_value = normalize_date(value)
                else:
                    normalized_value = value
                normalized[normalized_key] = normalized_value
    
    return normalized

class EquityTermsheetCaptureService:
    def add_termsheets(self, termsheets):
        """Add multiple termsheets to Firebase"""
        valid_termsheets = []
        skipped_count = 0
        
        for termsheet in termsheets:
            # Validate termsheet
            is_valid, message = validate_termsheet(termsheet)
            if not is_valid:
                print(f"Skipping invalid termsheet: {message}")
                skipped_count += 1
                continue
            
            # Normalize fields
            normalized_termsheet = normalize_termsheet_fields(termsheet)
            
            # Only keep allowed columns
            filtered_termsheet = {
                k: normalized_termsheet[k] 
                for k in allowed_columns 
                if k in normalized_termsheet
            }
            
            if filtered_termsheet:
                valid_termsheets.append(filtered_termsheet)
            else:
                skipped_count += 1
        
        if skipped_count > 0:
            print(f"Skipped {skipped_count} invalid termsheets")
        
        if not valid_termsheets:
            return []
        
        # Get existing termsheets
        existing = load_termsheets()
        
        # Add new termsheets to existing ones
        existing.extend(valid_termsheets)
        
        # Save all termsheets to Firebase
        save_termsheets(existing)
        return valid_termsheets

    def add_single_termsheet(self, termsheet):
        """Add a single termsheet to Firebase"""
        # Validate termsheet
        is_valid, message = validate_termsheet(termsheet)
        if not is_valid:
            raise ValueError(f"Invalid termsheet: {message}")
        
        # Normalize fields
        normalized_termsheet = normalize_termsheet_fields(termsheet)
        
        # Only keep allowed columns
        filtered_termsheet = {
            k: normalized_termsheet[k] 
            for k in allowed_columns 
            if k in normalized_termsheet
        }
        
        if not filtered_termsheet:
            raise ValueError("No valid fields found in termsheet")
        
        # Add to Firebase
        doc_id = add_termsheet(filtered_termsheet)
        return {"id": doc_id, **filtered_termsheet}

    def list_termsheets(self):
        """List all termsheets from Firebase"""
        return load_termsheets()

    def get_termsheet_by_trade_id(self, trade_id):
        """Get a specific termsheet by Trade ID from Firebase"""
        return get_termsheet_by_trade_id(trade_id)

equity_termsheet_capture_service = EquityTermsheetCaptureService() 