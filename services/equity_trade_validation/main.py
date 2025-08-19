from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services.equity_trade_validation.api import routes
import os
import services.firebase_client  # noqa: F401  # pylint: disable=unused-import  # Ensure Firebase is initialized

app = FastAPI(
    title="Trade Validation Service",
    description="Validates trade data using pre-defined rules",
    version="1.0.0"
)

# Optional: Allow frontend apps or other services to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(routes.router, prefix="/api/equity-validation")

# Serve validated_trades.json as a static file
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'db')
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Health check
@app.get("/")
def root():
    return {"message": "Trade Validation Service is up and running!"}

if __name__ == "__main__":
    import uvicorn
    import sys
    port = 8000
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])
    uvicorn.run("services.equity_trade_validation.main:app", host="0.0.0.0", port=port, reload=False)
