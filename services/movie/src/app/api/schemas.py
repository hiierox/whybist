from pydantic import BaseModel, Field, HttpUrl


class Country(BaseModel):
    country: str


class Genre(BaseModel):
    genre: str


class MovieSearchByKeywordSchema(BaseModel):
    film_id: int = Field(alias='filmId')
    name_ru: str | None = Field(default=None, alias='nameRu')
    name_en: str | None = Field(default=None, alias='nameEn')
    type: str | None = None
    year: str | None = None
    film_length: str | None = Field(default=None, alias='filmLength')
    countries: list[Country] | None = None
    genres: list[Genre] | None = None
    rating: str | None = None
    rating_vote_count: int | None = Field(default=None, alias='ratingVoteCount')
    poster_url_preview: HttpUrl | None = Field(default=None, alias='posterUrlPreview')


class MovieSearchByKeywordResponse(BaseModel):
    keyword: str
    page_count: int = Field(alias='pagesCount')
    films: list[MovieSearchByKeywordSchema]


class MovieSearchByIdResponse(BaseModel):
    id: int = Field(alias='kinopoiskId')
    name_ru: str | None = Field(default=None, alias='nameRu')
    name_en: str | None = Field(default=None, alias='nameEn')
    name_original: str | None = Field(default=None, alias='nameOriginal')
    poster_url: HttpUrl | None = Field(default=None, alias='posterUrl')
    rating_kinopoisk: float | None = Field(default=None, alias='ratingKinopoisk')
    rating_kinopoisk_vote_count: int | None = Field(
        default=None, alias='ratingKinopoiskVoteCount'
    )
    rating_imdb: float | None = Field(default=None, alias='ratingImdb')
    rating_imdb_vote_count: int | None = Field(
        default=None, alias='ratingImdbVoteCount'
    )
    web_url: HttpUrl | None = Field(default=None, alias='webUrl')
    year: int | None = None
    film_length: int | None = Field(default=None, alias='filmLength')
    description: str | None = None
    type: str | None = None
    rating_mpaa: str | None = Field(default=None, alias='ratingMpaa')
    countries: list[Country] | None = None
    genres: list[Genre] | None = None
    start_year: int | None = Field(default=None, alias='startYear')
    end_year: int | None = Field(default=None, alias='endYear')
    serial: bool | None = None
    short_film: bool | None = Field(default=None, alias='shortFilm')
    completed: bool | None = None
