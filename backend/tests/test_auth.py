import pytest
from rest_framework.authtoken.models import Token


class TestAuthenticationAPI:
    def test_register_returns_token(self, api_client, db):
        r = api_client.post('/api/auth/register/', {'username': 'newuser', 'password': 'a-good-pass-123'}, format='json')
        assert r.status_code == 201
        assert set(r.data) == {'token', 'username'}
        assert Token.objects.filter(key=r.data['token']).exists()

    def test_register_duplicate_username(self, api_client, user):
        r = api_client.post('/api/auth/register/', {'username': 'testuser', 'password': 'a-good-pass-123'}, format='json')
        assert r.status_code == 400

    def test_register_short_password(self, api_client, db):
        r = api_client.post('/api/auth/register/', {'username': 'x', 'password': 'short'}, format='json')
        assert r.status_code == 400

    def test_login_success(self, api_client, user):
        r = api_client.post('/api/auth/login/', {'username': 'testuser', 'password': 'testpass123'}, format='json')
        assert r.status_code == 200
        assert r.data['token'] == Token.objects.get(user=user).key

    def test_login_is_idempotent(self, api_client, user):
        d = {'username': 'testuser', 'password': 'testpass123'}
        first = api_client.post('/api/auth/login/', d, format='json').data['token']
        assert api_client.post('/api/auth/login/', d, format='json').data['token'] == first

    @pytest.mark.parametrize('payload', [
        {'username': 'wronguser', 'password': 'wrongpass'},
        {'username': 'testuser', 'password': 'wrongpass'},
    ])
    def test_login_invalid_credentials(self, api_client, user, payload):
        r = api_client.post('/api/auth/login/', payload, format='json')
        assert r.status_code == 401
        assert 'token' not in r.data

    @pytest.mark.parametrize('payload', [{'username': 'testuser'}, {'password': 'x'}, {}])
    def test_login_missing_fields(self, api_client, user, payload):
        assert api_client.post('/api/auth/login/', payload, format='json').status_code == 400

    def test_profile_requires_auth(self, api_client, db):
        assert api_client.get('/api/auth/profile/').status_code == 401

    def test_profile_returns_own_user(self, auth_client, user):
        r = auth_client.get('/api/auth/profile/')
        assert r.status_code == 200
        assert r.data['username'] == 'testuser'

    def test_invalid_token_rejected(self, api_client, db):
        api_client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        assert api_client.get('/api/datasets/').status_code == 401

    def test_logout_deletes_token(self, api_client, user):
        token = Token.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        assert api_client.post('/api/auth/logout/').status_code == 200
        assert not Token.objects.filter(user=user).exists()
        assert api_client.get('/api/datasets/').status_code == 401
