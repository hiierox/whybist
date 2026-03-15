from fastapi import APIRouter, Depends, Path, Query

from app.api.schemas import MovieSearchByIdResponse, MovieSearchByKeywordResponse
from app.dependencies import get_movie_service
from app.logic.movie_service import MovieService

router = APIRouter()


@router.get(
    '/film',
    response_model=MovieSearchByKeywordResponse,
    responses={
        401: {'description': 'Unauthorized (invalid API key)'},
        402: {'description': 'Daily request limit exceeded'},
        404: {'description': 'Movie not found'},
        429: {'description': 'Rate limit exceeded'},
        503: {'description': 'Upstream unavailable'},
    },
)
async def search_by_keyword(
    keyword: str = Query(..., pattern=r'.*\S.*'),
    page: int = Query(1, ge=1),
    movie_service: MovieService = Depends(get_movie_service),
) -> MovieSearchByKeywordResponse:
    return await movie_service.get_movie_by_keyword(keyword=keyword, page=page)


@router.get(
    '/film/{movie_id}',
    response_model=MovieSearchByIdResponse,
    responses={
        401: {'description': 'Unauthorized (invalid API key)'},
        402: {'description': 'Daily request limit exceeded'},
        404: {'description': 'Movie not found'},
        429: {'description': 'Rate limit exceeded'},
        503: {'description': 'Upstream unavailable'},
    },
)
async def get_movie_by_id(
    movie_id: int = Path(..., ge=1, le=9999999),
    movie_service: MovieService = Depends(get_movie_service),
) -> MovieSearchByIdResponse:
    return await movie_service.get_movie_by_id(movie_id=movie_id)
