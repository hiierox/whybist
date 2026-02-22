from datetime import UTC, datetime, timedelta

import jwt
from pydantic import UUID4

from app.config.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    settings,
)

from .exceptions import TokenValidationError


def create_token(
    data: dict[str, UUID4 | datetime | str], expires_delta: timedelta, token_type: str
) -> str:
    to_encode = data.copy()

    expire = datetime.now(UTC) + expires_delta
    to_encode.update({'exp': expire, 'iat': datetime.now(UTC), 'type': token_type})
    return jwt.encode(to_encode, settings.SECRET_KEY, ALGORITHM)


def create_access_token(user_id: UUID4) -> str:
    return create_token(
        data={'sub': user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type='access',
    )


def create_refresh_token(user_id: UUID4) -> str:
    return create_token(
        data={'sub': user_id},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        token_type='refresh',
    )


def decode_token(token: str) -> dict[str, str]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, ALGORITHM)
    except jwt.ExpiredSignatureError as e:
        raise TokenValidationError('Token expired') from e
    except jwt.InvalidTokenError as e:
        raise TokenValidationError('Invalid token') from e
