import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('email', 'username', 'password'),
    [
        pytest.param('test@example.com', 'usernick', 'password1', id='username=str'),
        pytest.param('mail@mail.mail', None, 'qwe!!!', id='username=None'),
    ],
)
async def test_register_success_201(client, email, username, password):
    request = {
        'email': email,
        'username': username,
        'password': password,
    }
    response = await client.post('/register', json=request)

    assert response.status_code == 201


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('email', 'username', 'password'),
    [
        pytest.param('test@example', 'usernick', 'password1', id='wrong_email'),
        pytest.param('mail@mail.mail', 150, 'qwe!!!', id='wrong_username'),
        pytest.param('mail@mail.mail', None, 'qwe', id='short_password'),
    ],
)
async def test_register_validation_error_422(client, email, username, password):
    request = {
        'email': email,
        'username': username,
        'password': password,
    }
    response = await client.post('/register', json=request)

    assert response.status_code == 422


@pytest.mark.parametrize(
    ('first_user', 'second_user', 'error_detail'),
    [
        pytest.param(
            {'email': 'same@test.co', 'username': 'user1', 'password': 'password'},
            {'email': 'same@test.co', 'username': 'user2', 'password': 'password'},
            'already exists',
            id='email_taken',
        ),
        pytest.param(
            {'email': 'user1@test.co', 'username': 'same_nick', 'password': 'password'},
            {'email': 'user2@test.co', 'username': 'same_nick', 'password': 'password'},
            'already exists',
            id='username_taken',
        ),
    ],
)
@pytest.mark.asyncio
async def test_register_duplicate_error_400(
    client, first_user, second_user, error_detail
):
    await client.post('/register', json=first_user)

    response = await client.post('/register', json=second_user)

    assert response.status_code == 400
    assert error_detail in response.json()['detail']


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('register_data', 'login_data'),
    [
        pytest.param(
            {'email': 'same@test.co', 'username': 'user1', 'password': 'password'},
            {'identifier': 'user1', 'password': 'password'},
            id='username_as_identifier',
        ),
        pytest.param(
            {'email': 'same@test.co', 'username': None, 'password': 'password'},
            {'identifier': 'same@test.co', 'password': 'password'},
            id='email_as_identifier',
        ),
    ],
)
async def test_login_success_200(client, register_data, login_data):
    await client.post('/register', json=register_data)

    response = await client.post('/login', json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('login_data'),
    [
        pytest.param(
            {'identifier': 'mail@mail.ail', 'password': 'password'}, id='wrong_email'
        ),
        pytest.param(
            {'identifier': 'email@mail.ail', 'password': 'aaaaaa'}, id='wrong_password'
        ),
    ],
)
async def test_login_unauthorized_401(client, login_data):
    await client.post(
        '/register', json={'email': 'email@mail.ail', 'password': 'password'}
    )

    response = await client.post('/login', json=login_data)

    assert response.status_code == 401


@pytest.mark.parametrize(
    'payload',
    [
        pytest.param({'identifier': 'test@mail.com'}, id='missing_password'),
        pytest.param({'password': 'password123'}, id='missing_identifier'),
        pytest.param({}, id='empty_body'),
    ],
)
@pytest.mark.asyncio
async def test_login_validation_error_422(client, payload):
    response = await client.post('/login', json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_me_success_200(client, user_factory):
    user, token = user_factory
    response = await client.get('/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json()['email'] == user['email']
    assert response.json()['username'] == user['username']


@pytest.mark.asyncio
async def test_get_me_unauthorized_401(client):
    response = await client.get('/me')
    assert response.status_code == 401


@pytest.mark.parametrize(
    ('current_password', 'new_password'),
    [
        pytest.param('password123', 'new_password_123', id='success_change'),
    ],
)
@pytest.mark.asyncio
async def test_change_password_success_200(
    client, user_factory, current_password, new_password
):
    user, token = user_factory

    response = await client.post(
        '/me/change-password',
        json={'current_password': current_password, 'new_password': new_password},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200
    assert 'access_token' in response.json()
    login_with_old_pass = await client.post(
        '/login', json={'identifier': f'{user['email']}', 'password': 'password123'}
    )
    assert login_with_old_pass.status_code == 401
    login_with_new_pass = await client.post('/login', json={'identifier': user['email'], 'password': new_password})
    assert login_with_new_pass.status_code == 200


@pytest.mark.parametrize(
    ('current_password', 'new_password'),
    [
        pytest.param('password', 'new_password_123', id='success_change'),
    ],
)
@pytest.mark.asyncio
async def test_change_password_wrong_current_password_401(
    client, user_factory, current_password, new_password
):
    user, token = user_factory

    response = await client.post(
        '/me/change-password',
        json={'current_password': current_password, 'new_password': new_password},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 401
    old_login = await client.post(
        '/login', json={'identifier': f'{user['email']}', 'password': 'password123'}
    )
    assert old_login.status_code == 200
    new_login = await client.post('/login', json={'identifier': user['email'], 'password': new_password})
    assert new_login.status_code == 401


@pytest.mark.parametrize(
    'update_payload',
    [
        pytest.param({'username': 'new_nick'}, id='update_username'),
    ],
)
@pytest.mark.asyncio
async def test_update_me(client, user_factory, update_payload):
    user, token = user_factory

    response = await client.patch(
        '/me', json=update_payload, headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json()['username'] == update_payload['username']
    old_login = await client.post(
        '/login', json={'identifier': f'{user['username']}', 'password': 'password123'}
    )
    assert old_login.status_code == 401
