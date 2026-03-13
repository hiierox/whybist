from typing import Any

from fastapi import APIRouter, Depends, Path, Query

from app.dependencies import get_movie_service
from app.logic.movie_service import MovieService

router = APIRouter()


@router.get('/film')
async def search_by_keyword(
    keyword: str = Query(..., pattern=r'.*\S.*'),
    page: int = Query(1, ge=1),
    movie_service: MovieService = Depends(get_movie_service),
) -> Any:
    return await movie_service.get_movie_by_keyword(keyword=keyword, page=page)


@router.get('/film/{movie_id}')
async def get_movie_by_id(
    movie_id: int = Path(..., ge=1, le=9999999),
    movie_service: MovieService = Depends(get_movie_service)
) -> Any:
    return await movie_service.get_movie_by_id(movie_id=movie_id)
