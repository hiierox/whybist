from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database.database import get_async_session
from app.logic.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def get_user_id_from_token(token: str = Depends(oauth2_scheme)) -> UUID4:
    try:
        payload = decode_token(token)
        user_id = payload.get('sub')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate token',
            )
        return UUID(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


def get_auth_service(session: AsyncSession = Depends(get_async_session)) -> AuthService:
    return AuthService(session)
