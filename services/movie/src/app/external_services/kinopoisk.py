from typing import Any

import httpx

from app.core.exceptions import (
    KinopoiskApiError,
    KinopoiskLimitExceededError,
    KinopoiskNotFoundError,
    KinopoiskRateLimitError,
    KinopoiskTransportError,
    KinopoiskUnauthorizedError,
)


class KinopoiskService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    @staticmethod
    def _extract_error_detail(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return (
                response.text or f'Kinopoisk API returned status {response.status_code}'
            )

        if isinstance(payload, dict):
            value = payload.get('message')
            if isinstance(value, str) and value.strip():
                return value

        return f'Kinopoisk API returned status {response.status_code}'

    def _raise_for_kinopoisk_error(self, response: httpx.Response) -> None:
        detail = self._extract_error_detail(response)

        error_map = {
            401: KinopoiskUnauthorizedError,
            402: KinopoiskLimitExceededError,
            404: KinopoiskNotFoundError,
            429: KinopoiskRateLimitError,
        }
        exc_cls = error_map.get(response.status_code, KinopoiskApiError)
        raise exc_cls(detail)

    async def _get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        try:
            response = await self.http_client.get(path, params=params)
        except httpx.HTTPError as e:
            raise KinopoiskTransportError('Kinopoisk API is Unavailable') from e

        if response.status_code != 200:
            self._raise_for_kinopoisk_error(response)

        try:
            payload = response.json()
        except ValueError as e:
            raise KinopoiskApiError(
                'Kinopoisk API returned invalid JSON payload'
            ) from e

        if not isinstance(payload, dict):
            raise KinopoiskApiError(
                'Kinopoisk API returned unexpected JSON payload'
            )

        return payload

    async def get_movie_by_keyword(self, params: dict[str, Any]) -> dict[str, Any]:
        return await self._get('/api/v2.1/films/search-by-keyword', params=params)

    async def get_movie_by_id(self, movie_id: int) -> dict[str, Any]:
        return await self._get(f'/api/v2.2/films/{movie_id}')
