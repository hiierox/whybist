import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.api.handler import router as kp_router
from app.config.config import settings
from app.core.exceptions import KinopoiskApiError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    http_client = httpx.AsyncClient(
        base_url='https://kinopoiskapiunofficial.tech',
        headers={
            'X-API-KEY': settings.KINOPOISK_API_KEY,
            'accept': 'application/json',
        },
        timeout=10.0,
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    )
    app.state.http_client = http_client

    redis_client = Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )
    app.state.redis_client = redis_client

    yield
    await http_client.aclose()
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(kp_router)


@app.exception_handler(KinopoiskApiError)
async def kinopoisk_api_error_handler(
    request: Request, exc: KinopoiskApiError
) -> JSONResponse:
    detail_by_code = {
        401: 'Internal service error',
        402: 'Daily request limit exceeded',
        404: 'Movie not found',
        429: 'RPS exceeded, try again later',
        503: 'Server temporary unavailable',
    }
    detail = detail_by_code.get(exc.status_code, 'External service error')

    if exc.status_code >= 500:
        logger.exception(
            f'Kinopoisk error on {request.method} {request.url.path}', exc_info=exc
        )
    else:
        logger.warning(
            f'Kinopoisk war on {request.method} {request.url.path}', exc_info=exc
        )

    return JSONResponse(status_code=exc.status_code, content={'detail': detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        f'Unhandled error on {request.method} {request.url.path}', exc_info=exc
    )
    return JSONResponse(
        status_code=500, content={'detail': 'Unexpected internal server error'}
    )
