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
