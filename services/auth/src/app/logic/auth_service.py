import bcrypt
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    Token,
    UserUpdateRequest,
)
from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import create_access_token, create_refresh_token
from app.database.models import User
from app.database.repository import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _check_password(request_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(request_password.encode(), hashed_password.encode())

    async def register(self, request: RegisterRequest) -> User:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(request.password.encode(), salt).decode('utf-8')

        try:
            async with self.session.begin():
                user_repo = UserRepository(self.session)
                user_data = User(
                    email=request.email,
                    username=request.username,
                    hashed_password=hashed_password,
                )
                await user_repo.create_user(user_data=user_data)
        except IntegrityError as e:
            raise UserAlreadyExistsError(
                'User with this email or username already exists'
            ) from e
        return user_data

    async def login(self, request: LoginRequest) -> Token:
        user_repo = UserRepository(self.session)
        user_data = await user_repo.get_user_by_email_or_username(request.identifier)
        if not user_data:
            raise InvalidCredentialsError('Invalid username or password')

        is_password_correct = self._check_password(
            request.password, user_data.hashed_password
        )
        if not is_password_correct:
            raise InvalidCredentialsError('Invalid username or password')

        access_token = create_access_token(user_id=user_data.id)
        refresh_token = create_refresh_token(user_id=user_data.id)
        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type='bearer'
        )

    async def change_password(
        self, user_id: UUID4, request: ChangePasswordRequest
    ) -> Token:
        async with self.session.begin():
            user_repo = UserRepository(self.session)
            user_data = await user_repo.get_user_by_id(user_id)
            if not user_data:
                raise UserNotFoundError('User not found')

            is_password_correct = self._check_password(
                request.current_password, user_data.hashed_password
            )
            if not is_password_correct:
                raise InvalidCredentialsError('Invalid password')

            hashed_password = bcrypt.hashpw(
                request.new_password.encode(), bcrypt.gensalt()
            ).decode('utf-8')

            await user_repo.update_user(user_data, hashed_password=hashed_password)
        access_token = create_access_token(user_id=user_data.id)
        refresh_token = create_refresh_token(user_id=user_data.id)
        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type='bearer'
        )

    async def change_email_or_username(
        self, user_id: UUID4, request: UserUpdateRequest
    ) -> User:
        to_update = request.model_dump(exclude_unset=True)
        try:
            async with self.session.begin():
                user_repo = UserRepository(self.session)
                user_data = await user_repo.get_user_by_id(user_id)
                if not user_data:
                    raise UserNotFoundError('User not found')
                if to_update:
                    await user_repo.update_user(user=user_data, **to_update)
            return user_data
        except IntegrityError as e:
            raise UserAlreadyExistsError(
                'User with this email or username already exists'
            ) from e
