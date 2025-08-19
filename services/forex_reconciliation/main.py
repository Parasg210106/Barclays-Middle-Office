from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.forex_reconciliation.api.routes import router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Forex Reconciliation Service is running"}

@app.get("/simple-test")
def simple_test():
    
    return {"message": "Simple test works"}

# Include the router

app.include_router(router, prefix="/api/forex-reconciliation")

