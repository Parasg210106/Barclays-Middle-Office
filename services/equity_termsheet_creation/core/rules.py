import json
import os

RULES_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../equity_trade_validation/core/rules_config.json')

def load_rules_config():
    with open(RULES_CONFIG_PATH, 'r') as f:
        return json.load(f)

rules_config = load_rules_config() 