from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.forex_trade_validation.api.routes import router

app = FastAPI(
    title="Forex Trade Validation Service",
    description="Validates and reconciles forex trade data between termsheet and captured sources",
    version="1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Forex Trade Validation Service is running",
        "version": "1.0",
        "endpoints": {
            "validate_trades": "/api/validate",
            "validate_single": "/api/validate/single",
            "get_results": "/api/results",
            "get_failed": "/api/results/failed",
            "get_passed": "/api/results/passed",
            "get_summary": "/api/summary",
            "get_trade": "/api/trade/{trade_id}",
            "clear_data": "/api/clear",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8016) 