from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config.config import settings
from app.database.database import Base, get_async_session
from app.service import app


@pytest.fixture
async def create_engine():
    """Create engine. Prepare database: drop all tables and create new ones
    (as a precausion)
    And dispose the engine at the end.

    Yields:
        engine: async engine
    """
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def connection(create_engine):
    """Take connection from engine and create manually controlled transaction
    in order to use "savepoint" mechanism.
    """
    connection = await create_engine.connect()
    transaction = await connection.begin()

    try:
        yield connection
    finally:
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()


@pytest.fixture
async def client(connection):
    async def override_get_async_session():
        async with AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode='create_savepoint'
        ) as session:
            yield session

    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def user_factory(client):
    """Фикстура для создания пользователя и получения токена доступа."""
    user_data = {
        'email': 'fixture@test.co',
        'username': 'fixture_user',
        'password': 'password123'
    }

    await client.post('/register', json=user_data)

    response = await client.post('/login', json={
        'identifier': user_data['email'],
        'password': user_data['password']
    })
    return user_data, response.json()['access_token']


@pytest.fixture
def mock_user_repo():
    with patch("app.logic.auth_service.UserRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_user_by_id = AsyncMock()
        repo.get_user_by_email_or_username = AsyncMock()
        repo.create_user = AsyncMock()
        repo.update_user = AsyncMock()
        yield repo_cls, repo


@asynccontextmanager
async def _tx_cm():
    yield

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.begin = _tx_cm
    return session

@pytest.fixture
def make_user():
    def _make_user(email="test@example.com", username="user1", hashed_password="hash"):
        from app.database.models import User
        return User(email=email, username=username, hashed_password=hashed_password)
    return _make_user