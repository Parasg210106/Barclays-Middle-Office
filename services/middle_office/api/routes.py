from fastapi import APIRouter, HTTPException
from services.firebase_client import get_firestore_client
from typing import List, Dict
import datetime

router = APIRouter()

# Define all columns for the consolidated table
CONSOLIDATED_COLUMNS = [
    'Account_ID', 'Account_No', 'Account_Status', 'Approval_Status', 'Base_Currency', 'Booking_Location',
    'Client_ID', 'Confirmation_Status', 'Counterparty', 'Currency_Pair', 'Custodian', 'Effective_Date',
    'Execution_Venue', 'Expense_Approval_Status', 'IBAN', 'KYC_Status', 'LEI', 'Method',
    'Netting_Eligibility', 'Portfolio', 'Product_Type', 'SWIFT', 'Sanctions_Screening',
    'Settlement_Currency', 'source', 'uploadedAt', 'uploadedBy',
    # Additional columns
    'Trade ID', 'Trader ID', 'Currency', 'Trade Date', 'K Y C Status', 'Validation Status',
    'Event Type', 'Event Status', 'INTERNAL VALUE', 'EXTERNAL VALUE', 'REPORTED TO', 'REASON'
]

@router.get("/consolidated/master-data", response_model=List[Dict])
def get_consolidated_master_data():
    db = get_firestore_client()
    # Fetch all base records
    nwm_docs = db.collection('NWM_Management').stream()
    nwm_data = [doc.to_dict() for doc in nwm_docs]
    # Fetch all additional data
    fx_capture = {doc.get('TradeID'): doc.to_dict() for doc in db.collection('fx_capture').stream()}
    fx_termsheet = {doc.get('TradeID'): doc.to_dict() for doc in db.collection('fx_termsheet').stream()}
    fx_validation = {doc.get('TradeID'): doc.to_dict() for doc in db.collection('fx_validation').stream()}
    fx_reconciliation = {doc.get('TradeID'): doc.to_dict() for doc in db.collection('fx_reconciliation').stream()}
    fx_lifecycle = {doc.get('TradeID'): doc.to_dict() for doc in db.collection('fx_lifecycle').stream()}
    consolidated = []
    for row in nwm_data:
        trade_id = row.get('Trade ID') or row.get('TradeID') or row.get('trade_id')
        merged = {col: row.get(col, '') for col in CONSOLIDATED_COLUMNS}
        # Merge additional columns
        if trade_id:
            capture = fx_capture.get(trade_id, {})
            termsheet = fx_termsheet.get(trade_id, {})
            validation = fx_validation.get(trade_id, {})
            reconciliation = fx_reconciliation.get(trade_id, {})
            lifecycle = fx_lifecycle.get(trade_id, {})
            merged['Trade ID'] = trade_id
            merged['Trader ID'] = capture.get('TraderID', '')
            merged['Currency'] = capture.get('CurrencyPair', '')
            merged['Trade Date'] = capture.get('TradeDate', '')
            merged['K Y C Status'] = capture.get('KYCCheck', '')
            merged['Validation Status'] = validation.get('ValidationStatus', '')
            merged['Event Type'] = lifecycle.get('EventType', '')
            merged['Event Status'] = lifecycle.get('EventStatus', '')
            merged['INTERNAL VALUE'] = reconciliation.get('InternalValue', '')
            merged['EXTERNAL VALUE'] = reconciliation.get('ExternalValue', '')
            merged['REPORTED TO'] = reconciliation.get('ReportedTo', '')
            merged['REASON'] = reconciliation.get('Reason', '')
        consolidated.append(merged)
    # Store in middle_office collection
    now = datetime.datetime.utcnow().isoformat()
    for row in consolidated:
        row['uploadedAt'] = now
        db.collection('middle_office').add(row)
    return consolidated 