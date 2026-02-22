import logging

from fastapi import FastAPI

from app.api.handler import router as auth_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(auth_router)
