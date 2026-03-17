from typing import cast

import httpx
from fastapi import Depends, Request
from redis.asyncio import Redis

from app.external_services.kinopoisk import KinopoiskService
from app.logic.movie_service import MovieService


def get_http_client(request: Request) -> httpx.AsyncClient:
    return cast(httpx.AsyncClient, request.app.state.http_client)


def get_kinopoisk_service(
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> KinopoiskService:
    return KinopoiskService(http_client=http_client)


def get_redis_client(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis_client)


def get_movie_service(
    kinopoisk_service: KinopoiskService = Depends(get_kinopoisk_service),
    redis_client: Redis = Depends(get_redis_client)
) -> MovieService:
    return MovieService(kinopoisk_service, redis_client)
