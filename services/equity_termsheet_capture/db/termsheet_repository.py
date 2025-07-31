import json
import os
from services.firebase_client import get_firestore_client

COLLECTION_NAME = "eq_termsheets"

def get_trade_id_from_termsheet(termsheet):
    """Extract Trade ID from termsheet using various possible field names"""
    trade_id_variations = [
        'Trade ID', 'TradeID', 'Trade_Id', 'Trade Id', 
        'tradeid', 'trade_id', 'trade id', 'trade id'
    ]
    
    for variation in trade_id_variations:
        if variation in termsheet and termsheet[variation]:
            return str(termsheet[variation]).strip()
    
    return None

def load_termsheets():
    """Load all termsheets from Firebase collection"""
    try:
        db = get_firestore_client()
        collection_ref = db.collection(COLLECTION_NAME)
        docs = collection_ref.stream()
        
        termsheets = []
        for doc in docs:
            termsheet_data = doc.to_dict()
            termsheet_data['id'] = doc.id  # Add document ID for reference
            termsheets.append(termsheet_data)
        
        return termsheets
    except Exception as e:
        print(f"Error loading termsheets from Firebase: {e}")
        return []

def save_termsheets(termsheets):
    """Save termsheets to Firebase collection using Trade ID as document name"""
    try:
        db = get_firestore_client()
        collection_ref = db.collection(COLLECTION_NAME)
        
        # Clear existing documents
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
        
        # Add new termsheets with Trade ID as document name
        for termsheet in termsheets:
            # Remove the 'id' field if it exists (it's added by load_termsheets)
            termsheet_data = {k: v for k, v in termsheet.items() if k != 'id'}
            
            # Get Trade ID for document name
            trade_id = get_trade_id_from_termsheet(termsheet_data)
            if trade_id:
                # Use Trade ID as document name
                doc_ref = collection_ref.document(trade_id)
                doc_ref.set(termsheet_data)
                print(f"Saved termsheet with Trade ID: {trade_id}")
            else:
                # Fallback to auto-generated ID if no Trade ID found
                collection_ref.add(termsheet_data)
                print("Saved termsheet with auto-generated ID (no Trade ID found)")
        
        print(f"Successfully saved {len(termsheets)} termsheets to Firebase collection '{COLLECTION_NAME}'")
    except Exception as e:
        print(f"Error saving termsheets to Firebase: {e}")
        raise

def add_termsheet(termsheet):
    """Add a single termsheet to Firebase collection using Trade ID as document name"""
    try:
        db = get_firestore_client()
        collection_ref = db.collection(COLLECTION_NAME)
        
        # Remove the 'id' field if it exists
        termsheet_data = {k: v for k, v in termsheet.items() if k != 'id'}
        
        # Get Trade ID for document name
        trade_id = get_trade_id_from_termsheet(termsheet_data)
        if trade_id:
            # Use Trade ID as document name
            doc_ref = collection_ref.document(trade_id)
            doc_ref.set(termsheet_data)
            print(f"Successfully added termsheet with Trade ID: {trade_id}")
            return trade_id
        else:
            # Fallback to auto-generated ID if no Trade ID found
            doc_ref = collection_ref.add(termsheet_data)
            print("Successfully added termsheet with auto-generated ID (no Trade ID found)")
            return doc_ref[1].id
        
    except Exception as e:
        print(f"Error adding termsheet to Firebase: {e}")
        raise

def get_termsheet_by_trade_id(trade_id):
    """Get a specific termsheet by Trade ID"""
    try:
        db = get_firestore_client()
        collection_ref = db.collection(COLLECTION_NAME)
        
        # Try to get document by Trade ID as document name first
        doc = collection_ref.document(trade_id).get()
        if doc.exists:
            termsheet_data = doc.to_dict()
            termsheet_data['id'] = doc.id
            return termsheet_data
        
        # Fallback: Query for termsheet with matching Trade ID field
        query = collection_ref.where('Trade ID', '==', trade_id).limit(1)
        docs = query.stream()
        
        for doc in docs:
            termsheet_data = doc.to_dict()
            termsheet_data['id'] = doc.id
            return termsheet_data
        
        return None
    except Exception as e:
        print(f"Error getting termsheet by Trade ID from Firebase: {e}")
        return None 