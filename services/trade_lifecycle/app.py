from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .api.routes import router
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:8080"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("filtered_trades", exist_ok=True)
os.makedirs("data", exist_ok=True)

app.mount("/filtered_trades", StaticFiles(directory="filtered_trades"), name="filtered_trades")

# Use the new templates path
templates = Jinja2Templates(directory="frontend/templates")

# Include the API router
app.include_router(router, prefix="/api/trade-lifecycle")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.trade_lifecycle.app:app", host="0.0.0.0", port=8024, reload=True)