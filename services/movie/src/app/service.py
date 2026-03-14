import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.handler import router as kp_router
from app.config.config import settings
from app.core.exceptions import (
    KinopoiskInvalidResponseError,
    KinopoiskLimitExceededError,
    KinopoiskNotFoundError,
    KinopoiskRateLimitError,
    KinopoiskTransportError,
    KinopoiskUnauthorizedError,
)

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

    yield
    await http_client.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(kp_router)


@app.exception_handler(KinopoiskLimitExceededError)
async def kinopoisk_limit_error_handler(
    request: Request, exc: KinopoiskLimitExceededError
) -> JSONResponse:
    logger.warning(
        f'Kinopoisk error on {request.method} {request.url.path}', exc_info=exc
    )
    return JSONResponse(
        status_code=exc.status_code, content={'detail': 'Daily request limit exceeded'}
    )


@app.exception_handler(KinopoiskNotFoundError)
async def kinopoisk_not_found_error_handler(
    request: Request, exc: KinopoiskNotFoundError
) -> JSONResponse:
    logger.warning(
        f'Kinopoisk error on {request.method} {request.url.path}', exc_info=exc
    )
    return JSONResponse(
        status_code=exc.status_code, content={'detail': 'Movie not found'}
    )


@app.exception_handler(KinopoiskTransportError)
async def kinopoisk_transport_error_handler(
    request: Request, exc: KinopoiskTransportError
) -> JSONResponse:
    logger.exception(
        f'Kinopoisk error on {request.method} {request.url.path}', exc_info=exc
    )
    return JSONResponse(
        status_code=exc.status_code, content={'detail': 'Server temporary unavailable'}
    )


@app.exception_handler(KinopoiskRateLimitError)
async def kinopoisk_rate_limit_error_handler(
    request: Request, exc: KinopoiskRateLimitError
) -> JSONResponse:
    logger.warning(
        f'Kinopoisk error on {request.method} {request.url.path}', exc_info=exc
    )
    return JSONResponse(
        status_code=exc.status_code, content={'detail': 'RPS exceeded, try again later'}
    )


@app.exception_handler(KinopoiskUnauthorizedError)
async def kinopoisk_unauthorized_error_handler(
    request: Request, exc: KinopoiskUnauthorizedError
) -> JSONResponse:
    logger.warning(
        f'Kinopoisk error on {request.method} {request.url.path}', exc_info=exc
    )
    return JSONResponse(
        status_code=exc.status_code, content={'detail': 'Internal service error'}
    )


@app.exception_handler(KinopoiskInvalidResponseError)
async def kinipoisk_invalid_response_handler(
    request: Request, exc: KinopoiskUnauthorizedError
) -> JSONResponse:
    logger.exception(
        f'Kinopoisk error on {request.method} {request.url.path}', exc_info=exc
    )
    return JSONResponse(
        status_code=exc.status_code, content={'detail': 'External service error'}
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        f'Unhandled error on {request.method} {request.url.path}', exc_info=exc
    )
    return JSONResponse(
        status_code=500, content={'detail': 'Unexcpected Internal server error'}
    )
