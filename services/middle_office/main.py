from fastapi import FastAPI
from services.middle_office.api.routes import router

app = FastAPI()
app.include_router(router) 