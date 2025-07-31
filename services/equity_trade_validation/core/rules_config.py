import json
import os

RULES_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'rules_config.json')
 
with open(RULES_CONFIG_PATH, 'r') as f:
    rules_config = json.load(f) 