import logging
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import services.firebase_client  # noqa: F401  # pylint: disable=unused-import  # Ensure Firebase is initialized
import requests

# Add the parent directory to the path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Equity Capture Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from services.equity_capture.api.routes import router
app.include_router(router)

# Add single trade POST endpoint for direct posting
from fastapi import Request
@app.post("/trades")
async def capture_trade_proxy(request: Request):
    trade = await request.json()
    from shared.models import Trade
    from services.equity_capture.services.capture_service import trade_capture_service
    try:
        return trade_capture_service.add_trade(Trade.parse_obj(trade))
    except Exception as e:
        return {"error": str(e)}

TERMSHEET_SERVICE_URL = "http://localhost:8010/termsheets"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 