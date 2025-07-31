import json

TRADE_FILE = "db/trades.json"

def capture_trade_data(trade_data):
    try:
        with open(TRADE_FILE, "r") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []

    existing.extend(trade_data)

    with open(TRADE_FILE, "w") as f:
        json.dump(existing, f, indent=2)
