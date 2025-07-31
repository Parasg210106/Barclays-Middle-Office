from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.equity_termsheet_capture.api import routes

app = FastAPI(title="Equity Termsheet Capture Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API router
app.include_router(routes.router)

# Remove or comment out the old /equity-termsheet-capture/bulk endpoint
# @app.post("/equity-termsheet-capture/bulk")
# def upload_equity_termsheets(termsheets: List[Dict[str, Any]] = Body(...)):
#     ...

if __name__ == "__main__":
    import uvicorn
    import sys
    port = 8000
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])
    uvicorn.run("services.equity_termsheet_capture.main:app", host="0.0.0.0", port=port, reload=False) 