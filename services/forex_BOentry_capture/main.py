import logging
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import services.firebase_client  # noqa: F401  # pylint: disable=unused-import  # Ensure Firebase is initialized

# Add the parent directory to the path to import shared modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="BOentry Capture Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from services.forex_BOentry_capture.api.routes import router
app.include_router(router)

print('[DEBUG] forex_capture main.py starting')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8020) 