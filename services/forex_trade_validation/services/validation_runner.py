import os
import sys
from typing import List, Dict
from services.forex_trade_validation.core.rules_engine import RulesEngine
from services.forex_trade_validation.db.validation_repository import ValidationRepository

class ValidationRunner:
    def __init__(self):
        # Get the directory path for the rules config
        current_dir = os.path.dirname(os.path.abspath(__file__))
        rules_config_path = os.path.join(current_dir, "..", "core", "rules_config.json")
        
        self.rules_engine = RulesEngine(rules_config_path)
        self.repository = ValidationRepository()

    def validate_trades(self, trades: List[Dict]) -> List[Dict]:
        """
        Validate a list of trades using the rules engine.
        
        Args:
            trades: List of trade dictionaries to validate
            
        Returns:
            List of validation results with TradeID, is_valid, and errors
        """
        try:
            # Run validation using the rules engine
            validation_results = self.rules_engine.validate_trades(trades)
            
            # Save results to the database
            self.repository.save_validation_results(validation_results)
            
            return validation_results
            
        except Exception as e:

            return []

    def validate_single_trade(self, trade: Dict) -> Dict:
        """
        Validate a single trade.
        
        Args:
            trade: Trade dictionary to validate
            
        Returns:
            Validation result with TradeID, is_valid, and errors
        """
        try:
            result = self.rules_engine.validate_trade(trade)
            
            # Update the database with the new result
            all_results = self.repository.get_all_validated_trades()
            
            # Remove existing result for this trade if it exists
            all_results = [r for r in all_results if r.get("TradeID") != result.get("TradeID")]
            
            # Add the new result
            all_results.append(result)
            
            # Save updated results
            self.repository.save_validation_results(all_results)
            
            return result
            
        except Exception as e:

            return {"TradeID": trade.get("TradeID", "UNKNOWN"), "is_valid": False, "errors": [str(e)]}

    def get_validation_summary(self) -> Dict:
        """
        Get a summary of validation results.
        
        Returns:
            Dictionary with counts of passed, failed, and total trades
        """
        all_trades = self.repository.get_all_validated_trades()
        passed_trades = self.repository.get_passed_trades()
        failed_trades = self.repository.get_failed_trades()
        
        return {
            "total_trades": len(all_trades),
            "passed_trades": len(passed_trades),
            "failed_trades": len(failed_trades),
            "success_rate": len(passed_trades) / len(all_trades) * 100 if all_trades else 0
        }

    def get_failed_trades(self) -> List[Dict]:
        """
        Get all trades that failed validation.
        
        Returns:
            List of failed trade validation results
        """
        return self.repository.get_failed_trades()

    def get_passed_trades(self) -> List[Dict]:
        """
        Get all trades that passed validation.
        
        Returns:
            List of passed trade validation results
        """
        return self.repository.get_passed_trades()

    def clear_validation_data(self) -> bool:
        """
        Clear all validation data from the database.
        
        Returns:
            True if successful, False otherwise
        """
        return self.repository.clear_database() 