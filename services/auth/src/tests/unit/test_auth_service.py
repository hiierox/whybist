from unittest.mock import AsyncMock, patch
from uuid import uuid4

import bcrypt
import pytest
from sqlalchemy.exc import IntegrityError

from app.api.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    UserUpdateRequest,
)
from app.core.exceptions import (
    InvalidCredentialsError,
    TokenValidationError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.database.models import User
from app.logic.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_success(mock_session, mock_user_repo):
    repo_cls, repo = mock_user_repo


    service = AuthService(mock_session)
    request = RegisterRequest(
        email='test@example.com',
        username='user1',
        password='password123',
    )

    result = await service.register(request)

    repo_cls.assert_called_once_with(mock_session)
    repo.create_user.assert_awaited_once()

    passed_user = repo.create_user.await_args.kwargs['user_data']
    assert passed_user.email == request.email
    assert passed_user.username == request.username
    assert passed_user.hashed_password != request.password
    assert bcrypt.checkpw(request.password.encode(), passed_user.hashed_password.encode())

    assert result is passed_user


@pytest.mark.asyncio
async def test_register_duplicate_raises_user_already_exists(mock_user_repo, mock_session):
    repo_cls, repo = mock_user_repo


    service = AuthService(mock_session)
    request = RegisterRequest(
        email='test@example.com',
        username='user1',
        password='password123',
    )

    repo.create_user = AsyncMock(
        side_effect=IntegrityError('INSERT ...',params={}, orig=Exception())
    )

    with pytest.raises(UserAlreadyExistsError):
        await service.register(request)

    repo_cls.assert_called_once_with(mock_session)
    repo.create_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_success(mock_user_repo, mock_session):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    register = User(
        email='test@example.com',
        username='user1',
    )

    request = LoginRequest(identifier='user1', password='password123')
    repo.get_user_by_email_or_username = AsyncMock(return_value=register)
    with patch.object(AuthService, '_check_password', return_value=True):
        with patch('app.logic.auth_service.create_access_token', return_value='access_123'):
            with patch('app.logic.auth_service.create_refresh_token', return_value='refresh_456'):
                result = await service.login(request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_email_or_username.assert_awaited_once_with('user1')
    assert result.access_token == 'access_123'
    assert result.refresh_token == 'refresh_456'
    assert result.token_type == 'bearer'


@pytest.mark.asyncio
async def test_login_user_not_found_raises_invalid_credentials(mock_user_repo, mock_session):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    request = LoginRequest(identifier='user1', password='password123')
    repo.get_user_by_email_or_username = AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentialsError):
        await service.login(request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_email_or_username.assert_awaited_once_with('user1')


@pytest.mark.asyncio
async def test_login_wrong_password_raises_invalid_credentials(mock_user_repo, mock_session, make_user):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user = make_user(hashed_password='fake_hash')
    request = LoginRequest(identifier='user1', password='password123')
    repo.get_user_by_email_or_username = AsyncMock(return_value=user)
    with patch.object(AuthService, '_check_password', return_value=False):
        with pytest.raises(InvalidCredentialsError):
            await service.login(request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_email_or_username.assert_awaited_once_with('user1')


@pytest.mark.asyncio
async def test_get_user_by_id_success(mock_user_repo, mock_session, make_user):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user_id = uuid4()
    user = make_user()
    repo.get_user_by_id = AsyncMock(return_value=user)

    result = await service.get_user_by_id(user_id)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_id.assert_awaited_once_with(user_id)
    assert result == user


@pytest.mark.asyncio
async def test_get_user_by_id_not_found_raises_user_not_found(mock_user_repo, mock_session):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user_id = uuid4()
    repo.get_user_by_id = AsyncMock(return_value=None)

    with pytest.raises(UserNotFoundError):
        await service.get_user_by_id(user_id)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_id.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_change_password_success(mock_user_repo, mock_session, make_user):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user_id = uuid4()
    user = make_user(hashed_password=bcrypt.hashpw(b'oldpass123', bcrypt.gensalt()).decode())
    user.id = user_id
    request = ChangePasswordRequest(current_password='oldpass123', new_password='newpass123')
    repo.get_user_by_id = AsyncMock(return_value=user)

    with patch('app.logic.auth_service.create_access_token', return_value='access_123'):
        with patch('app.logic.auth_service.create_refresh_token', return_value='refresh_456'):
            result = await service.change_password(user_id, request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_id.assert_awaited_once_with(user_id)
    repo.update_user.assert_awaited_once()
    update_args = repo.update_user.await_args
    assert update_args.args[0] is user
    assert update_args.kwargs['hashed_password'] != 'newpass123'
    assert bcrypt.checkpw(
        b'newpass123', update_args.kwargs['hashed_password'].encode()
    )
    assert result.access_token == 'access_123'
    assert result.refresh_token == 'refresh_456'
    assert result.token_type == 'bearer'


@pytest.mark.asyncio
async def test_change_password_user_not_found_raises_user_not_found(mock_user_repo, mock_session):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user_id = uuid4()
    request = ChangePasswordRequest(current_password='oldpass123', new_password='newpass123')
    repo.get_user_by_id = AsyncMock(return_value=None)

    with pytest.raises(UserNotFoundError):
        await service.change_password(user_id, request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_id.assert_awaited_once_with(user_id)
    repo.update_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_change_password_wrong_current_password_raises_invalid_credentials(
    mock_user_repo, mock_session, make_user
):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user_id = uuid4()
    user = make_user(hashed_password=bcrypt.hashpw(b'oldpass123', bcrypt.gensalt()).decode())
    request = ChangePasswordRequest(current_password='wrongpass123', new_password='newpass123')
    repo.get_user_by_id = AsyncMock(return_value=user)

    with pytest.raises(InvalidCredentialsError):
        await service.change_password(user_id, request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_id.assert_awaited_once_with(user_id)
    repo.update_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_change_email_or_username_success(mock_user_repo, mock_session, make_user):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user_id = uuid4()
    user = make_user(email='old@test.com', username='old_name')
    request = UserUpdateRequest(email='new@test.com', username='new_name')
    repo.get_user_by_id = AsyncMock(return_value=user)

    result = await service.change_email_or_username(user_id, request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_id.assert_awaited_once_with(user_id)
    repo.update_user.assert_awaited_once_with(user=user, email='new@test.com', username='new_name')
    assert result == user


@pytest.mark.asyncio
async def test_change_email_or_username_without_updates_does_not_call_update_user(
    mock_user_repo, mock_session, make_user
):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user_id = uuid4()
    user = make_user()
    request = UserUpdateRequest()
    repo.get_user_by_id = AsyncMock(return_value=user)

    result = await service.change_email_or_username(user_id, request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_id.assert_awaited_once_with(user_id)
    repo.update_user.assert_not_awaited()
    assert result == user


@pytest.mark.asyncio
async def test_change_email_or_username_user_not_found_raises_user_not_found(
    mock_user_repo, mock_session
):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user_id = uuid4()
    request = UserUpdateRequest(email='new@test.com')
    repo.get_user_by_id = AsyncMock(return_value=None)

    with pytest.raises(UserNotFoundError):
        await service.change_email_or_username(user_id, request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_id.assert_awaited_once_with(user_id)
    repo.update_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_change_email_or_username_duplicate_raises_user_already_exists(
    mock_user_repo, mock_session, make_user
):
    repo_cls, repo = mock_user_repo

    service = AuthService(mock_session)
    user_id = uuid4()
    user = make_user()
    request = UserUpdateRequest(email='duplicate@test.com')
    repo.get_user_by_id = AsyncMock(return_value=user)
    repo.update_user = AsyncMock(
        side_effect=IntegrityError('UPDATE ...', params={}, orig=Exception())
    )

    with pytest.raises(UserAlreadyExistsError):
        await service.change_email_or_username(user_id, request)

    repo_cls.assert_called_once_with(mock_session)
    repo.get_user_by_id.assert_awaited_once_with(user_id)
    repo.update_user.assert_awaited_once_with(user=user, email='duplicate@test.com')


@pytest.mark.asyncio
async def test_refresh_token_success(mock_session):
    service = AuthService(mock_session)
    user_id = uuid4()
    request = RefreshRequest(refresh_token='valid_refresh_token')

    with patch(
        'app.logic.auth_service.decode_token',
        return_value={'type': 'refresh', 'sub': str(user_id)}
    ):
        with patch('app.logic.auth_service.create_access_token', return_value='access_123'):
            with patch('app.logic.auth_service.create_refresh_token', return_value='refresh_456'):
                result = await service.refresh_token(request)

    assert result.access_token == 'access_123'
    assert result.refresh_token == 'refresh_456'
    assert result.token_type == 'bearer'


@pytest.mark.asyncio
async def test_refresh_token_invalid_token_raises_invalid_credentials(mock_session):
    service = AuthService(mock_session)
    request = RefreshRequest(refresh_token='invalid_refresh_token')

    with patch(
        'app.logic.auth_service.decode_token',
        side_effect=TokenValidationError('Invalid token'),
    ):
        with pytest.raises(InvalidCredentialsError):
            await service.refresh_token(request)
