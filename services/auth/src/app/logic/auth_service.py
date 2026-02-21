import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import LoginRequest, RegisterRequest
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.database.models import User
from app.database.repository import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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

    async def login(self, login_data: LoginRequest) -> User:
        user_repo = UserRepository(self.session)
        user_data = await user_repo.get_user_by_email_or_username(login_data.identifier)
        if not user_data:
            raise InvalidCredentialsError('Invalid username or password')

        is_password_correct = bcrypt.checkpw(
            login_data.password.encode(), user_data.hashed_password.encode()
        )
        if not is_password_correct:
            raise InvalidCredentialsError('Invalid username or password')

        return user_data
