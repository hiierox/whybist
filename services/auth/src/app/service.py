import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.handler import router as auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()
app.include_router(auth_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        'Unhandled error on %s %s', request.method, request.url.path, exc_info=exc
    )
    return JSONResponse(status_code=500, content={'detail': 'Internal server error'})
