from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from app.api.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    Token,
    UserResponse,
    UserUpdateRequest,
)
from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.dependencies import get_auth_service, get_user_id_from_token
from app.logic.auth_service import AuthService

router = APIRouter()


@router.post(
    '/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    request: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """Endpoint for registration  
    Args:    
        request (RegisterRequest): email, username(optinal), password  
        auth_service (AuthService): Defaults to Depends(get_auth_service).

    Raises:  
        HTTPException: 400 UserAlredyExists if email OR username already exists. So user
        can't actually understand what specifically taken.  
        HTTPException: BaseException - Unexpected error

    Returns:
        UserResponse: User object without password 
    """
    try:
        return await auth_service.register(request)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unexpected error during registration',
        ) from e


@router.post('/login', response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(
    request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    """Endpoint for login  

    Args:  
        request (LoginRequest): email or username, password  
        auth_service (AuthService): Defaults to Depends(get_auth_service).  

    Raises:  
        HTTPException: status 401 - invalid credentials  
        HTTPException: status 500 - unexpected error  

    Returns:  
        Token: access and refresh tokens + token_type
    """
    try:
        return await auth_service.login(request)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unexpected error during login',
        ) from e


@router.get('/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(
    user_id: UUID4 = Depends(get_user_id_from_token),
    auth_service: AuthService = Depends(get_auth_service)
    ) -> Any:
    """Returns User object with public info  

    Args:  
        user_id (UUID4): Defaults to Depends(get_user_id_from_token).    
        auth_service (AuthService): Defaults to Depends(get_auth_service).  

    Raises:  
        HTTPException: status 404 - user not found  
        HTTPException: status 500 - unexpected error  

    Returns:  
        UserResponse:  User object without password  
    """
    try:
        return await auth_service.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unexpected error during getting user',
        ) from e


@router.post(
        '/me/change-password', response_model=Token, status_code=status.HTTP_200_OK
        )
async def change_password(
    request: ChangePasswordRequest,
    user_id: UUID4 = Depends(get_user_id_from_token),
    auth_service: AuthService = Depends(get_auth_service)
    ) -> Token:
    """Endpoint for changing password  

    Args:  
        request (ChangePasswordRequest): current password and new one   
        user_id (UUID4): Defaults to Depends(get_user_id_from_token).  
        auth_service (AuthService): Defaults to Depends(get_auth_service).  

    Raises:  
        HTTPException: status 401 - wrong password  
        HTTPException: status 404 - user with this id (from token) not found  
        HTTPException: status 500 - unexpected error  

    Returns:  
        Token: access and refresh tokens + token_type
    """
    try:
        return await auth_service.change_password(user_id, request)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unexpected error during password changing',
        ) from e


@router.patch('/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    request: UserUpdateRequest,
    user_id: UUID4 = Depends(get_user_id_from_token),
    auth_service: AuthService = Depends(get_auth_service)
    ) -> Any:
    """Endpoint for updating user data

    Args:  
        request (UserUpdateRequest): email and/or username  
        user_id (UUID4): Defaults to Depends(get_user_id_from_token).  
        auth_service (AuthService): Defaults to Depends(get_auth_service).

    Raises:  
        HTTPException: status 400 - username or email already taken  
        HTTPException: status 500 - unexpected error 

    Returns:  
        UserResponse: User object without password  
    """
    try:
        return await auth_service.change_email_or_username(user_id, request)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unexpected error during credentials change',
        ) from e
