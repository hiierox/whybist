from app.api.schemas import MovieSearchByIdResponse, MovieSearchByKeywordResponse
from app.external_services.kinopoisk import KinopoiskService


class MovieService:
    def __init__(self, kinopoisk_service: KinopoiskService) -> None:
        self.kinopoisk_service = kinopoisk_service

    async def get_movie_by_keyword(
        self, keyword: str, page: int = 1
    ) -> MovieSearchByKeywordResponse:
        raw = await self.kinopoisk_service.get_movie_by_keyword(
            params={'keyword': keyword, 'page': page}
        )
        return MovieSearchByKeywordResponse.model_validate(raw)

    async def get_movie_by_id(self, movie_id: int) -> MovieSearchByIdResponse:
        raw = await self.kinopoisk_service.get_movie_by_id(movie_id=movie_id)
        return MovieSearchByIdResponse.model_validate(raw)
