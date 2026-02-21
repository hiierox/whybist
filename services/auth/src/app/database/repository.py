from typing import Any

from pydantic import UUID4
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_id(self, user_id: UUID4) -> User | None:
        return await self.session.get(User, user_id)

    async def get_user_by_email_or_username(self, identifier: str) -> User | None:
        query = select(User).where(
            or_(User.email == identifier, User.username == identifier)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: User) -> User:
        self.session.add(user_data)
        await self.session.flush()
        return user_data

    async def update_user(self, user: User, **user_data: Any) -> User:
        for key, value in user_data.items():
            setattr(user, key, value)
        await self.session.flush()
        return user
