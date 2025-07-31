import subprocess
import sys
import os
import fastapi
import pydantic

# List of service entry points with their ports
services = [
    ("services.equity_capture.main", 8001),
    ("services.forex_capture.main", 8002),
    ("services.forex_systemA_capture.main", 8017),
    ("services.forex_systemB_capture.main", 8018),
    ("services.forex_FOentry_capture.main", 8019),
    ("services.forex_BOentry_capture.main", 8020),
    ("services.equity_systemA_capture.main", 8021),
    ("services.equity_systemB_capture.main", 8022),
    ("services.equity_FOentry_capture.main", 8027),
    ("services.equity_BOentry_capture.main", 8023),
    ("services.equity_trade_validation.main", 8011),
    ("services.equity_termsheet_capture.main", 8013),
    ("services.forex_termsheet_capture.main", 8014),
    ("services.forex_trade_validation.main", 8016),
    ("services.trade_lifecycle.app", 8024),
    ("services.forex_reconciliation.main", 8025),
    ("services.equity_reconciliation.main", 8026),
]

processes = []

try:
    for service, port in services:
        print(f"Starting {service} on port {port}...")
        p = subprocess.Popen([
            sys.executable, "-m", "uvicorn", f"{service}:app",
            "--host", "0.0.0.0", "--port", str(port), "--reload"
        ])
        processes.append(p)
    print("All services started. Press Ctrl+C to stop.")
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("Stopping all services...")
    for p in processes:
        p.terminate()
    for p in processes:
        p.wait()
    print("All services stopped.")

print(fastapi.__version__)
print(pydantic.__version__) 