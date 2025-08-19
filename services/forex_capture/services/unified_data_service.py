from services.firebase_client import get_firestore_client
from services.forex_capture.models import Forex
from typing import Dict, Any, Optional, List
import logging
import uuid

logger = logging.getLogger(__name__)

class UnifiedDataService:
    def __init__(self):
        self.db = get_firestore_client()
        self.collection_name = "unified_data"
    
    def update_unified_data_with_forex_trade(self, forex_trade: Forex, client_id: str) -> bool:
        """
        Update the unified_data collection with forex trade data.
        Uses the provided client_id to find and update the correct document.
        
        Args:
            forex_trade: The Forex trade object to use for updating unified_data
            client_id: The client ID selected from the frontend dropdown
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        # Generate unique execution ID to track this specific call
        execution_id = str(uuid.uuid4())[:8]
        
        try:
            if not client_id or not client_id.strip():
                logger.warning(f"[{execution_id}] No client_id provided for trade {forex_trade.TradeID}")
                return False
            
            client_id = client_id.strip()
            logger.info(f"[{execution_id}] Looking for unified_data document with ClientID_Forex: {client_id}")
            
            # Find the document in unified_data collection by ClientID_Forex
            docs = self.db.collection(self.collection_name).where("ClientID_Forex", "==", client_id).stream()
            doc_ref = None
            
            for doc in docs:
                doc_ref = doc.reference
                break
            
            if not doc_ref:
                logger.warning(f"[{execution_id}] No unified_data document found for ClientID_Forex: {client_id}")
                return False
            
            # Get the existing document data
            existing_doc = doc_ref.get()
            if not existing_doc.exists:
                logger.warning(f"[{execution_id}] Document reference exists but document doesn't exist for ClientID_Forex: {client_id}")
                return False
            
            existing_data = existing_doc.to_dict()
            logger.info(f"[{execution_id}] Found existing unified_data document: {existing_doc.id}")
            
            # Use the helper method to update the document
            return self._update_single_document(forex_trade, doc_ref, existing_data, f"document {existing_doc.id}")
            
        except Exception as e:
            logger.error(f"[{execution_id}] Error updating unified_data for trade {forex_trade.TradeID}: {str(e)}")
            return False
    
    def _find_case_insensitive_field(self, data_dict: dict, field_name: str) -> str:
        """
        Find a field name in the data dictionary with case-insensitive matching
        
        Args:
            data_dict: The dictionary to search in
            field_name: The field name to find
            
        Returns:
            The actual field name if found, None otherwise
        """
        field_name_lower = field_name.lower()
        for key in data_dict.keys():
            if key.lower() == field_name_lower:
                return key
        return None
    
    def get_unified_data_by_client_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get unified_data document by ClientID_Forex
        
        Args:
            client_id: The client ID to search for
            
        Returns:
            Dict containing the document data or None if not found
        """
        try:
            docs = self.db.collection(self.collection_name).where("ClientID_Forex", "==", client_id).stream()
            
            for doc in docs:
                return doc.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting unified_data for ClientID_Forex {client_id}: {str(e)}")
            return None

    def update_unified_data_with_bulk_forex_trades(self, forex_trades: List[Forex], client_id: str) -> bool:
        """
        Update the unified_data collection with multiple forex trades by creating duplicate documents.
        Creates one document per trade, preserving existing data in all documents.
        
        Args:
            forex_trades: List of Forex trade objects to use for updating unified_data
            client_id: The client ID selected from the frontend dropdown
            
        Returns:
            bool: True if all updates were successful, False otherwise
        """
        # Generate unique execution ID to track this specific call
        execution_id = str(uuid.uuid4())[:8]
        
        try:
            if not client_id or not client_id.strip():
                logger.warning(f"[{execution_id}] No client_id provided for bulk trades")
                return False
            
            if not forex_trades or len(forex_trades) == 0:
                logger.warning(f"[{execution_id}] No trades provided for bulk update")
                return False
            
            client_id = client_id.strip()
            logger.info(f"[{execution_id}] Processing {len(forex_trades)} trades for unified_data update with ClientID_Forex: {client_id}")
            
            # Find the original document in unified_data collection by ClientID_Forex
            docs = self.db.collection(self.collection_name).where("ClientID_Forex", "==", client_id).stream()
            original_doc_ref = None
            
            for doc in docs:
                original_doc_ref = doc.reference
                break
            
            if not original_doc_ref:
                logger.warning(f"[{execution_id}] No unified_data document found for ClientID_Forex: {client_id}")
                return False
            
            # Get the original document data
            original_doc = original_doc_ref.get()
            if not original_doc.exists:
                logger.warning(f"[{execution_id}] Document reference exists but document doesn't exist for ClientID_Forex: {client_id}")
                return False
            
            original_data = original_doc.to_dict()
            logger.info(f"[{execution_id}] Found original unified_data document: {original_doc.id}")
            
            # Create all duplicate documents first, then update each with trade data
            document_refs = []
            
            # First trade will use the original document
            document_refs.append((original_doc_ref, f"original document {original_doc.id}"))
            
            # Create duplicate documents for subsequent trades
            for i in range(1, len(forex_trades)):
                try:
                    # Create duplicate data (copy of original, before any trade updates)
                    duplicate_data = original_data.copy()
                    
                    # Create new document with random ID
                    new_doc_ref = self.db.collection(self.collection_name).document()
                    logger.info(f"[{execution_id}] Creating duplicate document {i+1} with ID: {new_doc_ref.id}")
                    
                    # Write the duplicate document to Firestore with original data
                    new_doc_ref.set(duplicate_data)
                    logger.info(f"[{execution_id}] Successfully created duplicate document {i+1} with ID: {new_doc_ref.id}")
                    
                    # Add to our list of documents to update
                    document_refs.append((new_doc_ref, f"duplicate document {i+1}"))
                    
                except Exception as e:
                    logger.error(f"[{execution_id}] Error creating duplicate document {i+1}: {str(e)}")
                    return False
            
            # Now update each document with its respective trade data
            success_count = 0
            for i, (doc_ref, doc_description) in enumerate(document_refs):
                try:
                    forex_trade = forex_trades[i]
                    
                    # Get the current document data (either original or duplicate)
                    if i == 0:
                        # For original document, use original_data
                        current_doc_data = original_data
                        logger.info(f"[{execution_id}] Using original data for {doc_description}")
                        logger.info(f"[{execution_id}] Original data TradeID: {current_doc_data.get('TradeID', 'NOT_FOUND')}")
                    else:
                        # For duplicate documents, get the data we just created
                        current_doc_data = doc_ref.get().to_dict()
                        logger.info(f"[{execution_id}] Using duplicate data for {doc_description}")
                        logger.info(f"[{execution_id}] Duplicate data TradeID: {current_doc_data.get('TradeID', 'NOT_FOUND')}")
                        logger.info(f"[{execution_id}] Duplicate data keys: {list(current_doc_data.keys())[:5]}...")
                    
                    logger.info(f"[{execution_id}] About to update {doc_description} with trade {forex_trade.TradeID}")
                    success = self._update_single_document(forex_trade, doc_ref, current_doc_data, doc_description)
                    
                    if success:
                        success_count += 1
                        logger.info(f"[{execution_id}] Successfully processed trade {i+1}/{len(forex_trades)} in {doc_description}")
                    else:
                        logger.error(f"[{execution_id}] Failed to process trade {i+1}/{len(forex_trades)} in {doc_description}")
                        
                except Exception as e:
                    logger.error(f"[{execution_id}] Error processing trade {i+1}/{len(forex_trades)} in {doc_description}: {str(e)}")
            
            logger.info(f"[{execution_id}] Bulk update complete: {success_count}/{len(forex_trades)} trades processed successfully")
            return success_count == len(forex_trades)
            
        except Exception as e:
            logger.error(f"[{execution_id}] Error in bulk unified_data update: {str(e)}")
            return False
    
    def _update_single_document(self, forex_trade: Forex, doc_ref, existing_data: dict, doc_description: str) -> bool:
        """
        Update a single document with trade data (existing logic)
        
        Args:
            forex_trade: The Forex trade object
            doc_ref: Reference to the document to update
            existing_data: Existing document data
            doc_description: Description for logging
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        # Generate unique execution ID to track this specific call
        execution_id = str(uuid.uuid4())[:8]
        
        try:
            # Convert forex trade to dict for easier processing
            trade_data = forex_trade.dict(by_alias=True)
            
            # Debug: Log the trade data being processed
            logger.info(f"[{execution_id}] Processing trade data for TradeID: {trade_data.get('TradeID', 'NOT_FOUND')} in {doc_description}")
            logger.info(f"[{execution_id}] Trade data keys: {list(trade_data.keys())[:5]}...")
            logger.info(f"[{execution_id}] Existing data TradeID: {existing_data.get('TradeID', 'NOT_FOUND')}")
            
            # Create merged data - only fill empty slots, don't overwrite existing data
            merged_data = existing_data.copy()
            updated_fields = []
            
            for field_name, field_value in trade_data.items():
                # Skip empty values but allow TradeID to be updated
                if not field_value or field_value == "":
                    logger.debug(f"[{execution_id}] Skipping empty field: {field_name}")
                    continue
                
                # Check for case-insensitive field name matches
                existing_field_name = self._find_case_insensitive_field(existing_data, field_name)
                
                # Only update if the field is empty, null, or doesn't exist in existing data
                if (existing_field_name is None or 
                    existing_data[existing_field_name] is None or 
                    existing_data[existing_field_name] == "" or
                    existing_data[existing_field_name] == "N/A"):
                    
                    # Use the original field name from trade data
                    merged_data[field_name] = field_value
                    updated_fields.append(field_name)
                    logger.info(f"[{execution_id}] Will update field '{field_name}' to '{field_value}' in {doc_description}")
                    
                    # Special logging for TradeID updates
                    if field_name == "TradeID":
                        logger.info(f"[{execution_id}] Updating TradeID field to: {field_value} in {doc_description}")
                        if existing_field_name:
                            logger.info(f"[{execution_id}] Previous TradeID value was: {existing_data[existing_field_name]}")
                        else:
                            logger.info(f"[{execution_id}] TradeID field did not exist in unified_data, adding new field")
                else:
                    logger.info(f"[{execution_id}] Field '{field_name}' already has value: '{existing_data[existing_field_name]}', skipping update in {doc_description}")
            
            if not updated_fields:
                logger.info(f"[{execution_id}] No new fields to update in {doc_description}")
                # For duplicate documents, we still want to confirm the document exists
                if "duplicate document" in doc_description:
                    logger.info(f"[{execution_id}] Duplicate document {doc_description} created successfully with original data")
                return True
            
            # Update the document with merged data
            logger.info(f"[{execution_id}] Updating {doc_description} with merged data containing TradeID: {merged_data.get('TradeID', 'NOT_FOUND')}")
            doc_ref.set(merged_data)
            logger.info(f"[{execution_id}] Successfully updated {doc_description} with {len(updated_fields)} new fields: {updated_fields}")
            
            # Log if TradeID was updated
            if "TradeID" in updated_fields:
                logger.info(f"[{execution_id}] TradeID field was updated in {doc_description}")
            
            return True
            
        except Exception as e:
            logger.error(f"[{execution_id}] Error updating {doc_description}: {str(e)}")
            return False

# Create a singleton instance
unified_data_service = UnifiedDataService()
