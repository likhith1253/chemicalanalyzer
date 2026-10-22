"""Regression tests for authorization, error handling and configuration hardening."""
import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError

PROTECTED = [
    ('get', '/api/datasets/'),
    ('get', '/api/datasets/1/'),
    ('get', '/api/datasets/1/report/pdf/'),
    ('get', '/api/datasets/1/analyze/'),
    ('post', '/api/upload/'),
    ('get', '/api/auth/profile/'),
    ('post', '/api/auth/logout/'),
]


@pytest.mark.parametrize('method,url', PROTECTED)
def test_protected_endpoints_require_authentication(api_client, db, method, url):
    assert getattr(api_client, method)(url).status_code == 401


class TestOwnership:
    """IDOR: user B must not reach user A's dataset by guessing its id."""

    def test_detail_hidden_from_other_user(self, other_client, equipment_dataset):
        assert other_client.get(f'/api/datasets/{equipment_dataset.id}/').status_code == 404

    def test_pdf_hidden_from_other_user(self, other_client, equipment_dataset):
        assert other_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/').status_code == 404

    def test_analyze_hidden_from_other_user(self, other_client, equipment_dataset):
        assert other_client.get(f'/api/datasets/{equipment_dataset.id}/analyze/').status_code == 404

    def test_list_excludes_other_users_datasets(self, other_client, equipment_dataset):
        assert other_client.get('/api/datasets/').data == []


class TestNoDefaultAdmin:
    def test_no_default_admin_account_is_created(self, db):
        assert not User.objects.filter(username='admin').exists()

    def test_create_admin_requires_env(self, db, monkeypatch):
        monkeypatch.delenv('ADMIN_USERNAME', raising=False)
        monkeypatch.delenv('ADMIN_PASSWORD', raising=False)
        with pytest.raises(CommandError):
            call_command('create_admin')

    def test_create_admin_uses_env_credentials(self, db, monkeypatch):
        monkeypatch.setenv('ADMIN_USERNAME', 'ops')
        monkeypatch.setenv('ADMIN_PASSWORD', 'from-env-only-123')
        call_command('create_admin')
        user = User.objects.get(username='ops')
        assert user.is_superuser and user.check_password('from-env-only-123')


class TestErrorLeakage:
    def test_analyze_does_not_leak_internal_error(self, auth_client, equipment_dataset, monkeypatch):
        def boom(_):
            raise RuntimeError('secret-internal-detail /srv/path')
        monkeypatch.setattr('equipment.views.generate_ai_insights', boom)
        r = auth_client.get(f'/api/datasets/{equipment_dataset.id}/analyze/')
        assert r.status_code == 500
        assert 'secret-internal-detail' not in r.content.decode()

    def test_ai_failure_returns_503_without_upstream_text(self, auth_client, equipment_dataset, monkeypatch):
        from equipment.services import AIGenerationError

        def fail(_):
            raise AIGenerationError('upstream said key=abc123')
        monkeypatch.setattr('equipment.views.generate_ai_insights', fail)
        r = auth_client.get(f'/api/datasets/{equipment_dataset.id}/analyze/')
        assert r.status_code == 503
        assert 'abc123' not in r.content.decode()


class TestThrottling:
    def test_login_is_rate_limited(self, api_client, user):
        codes = [
            api_client.post('/api/auth/login/', {'username': 'testuser', 'password': 'bad'}, format='json').status_code
            for _ in range(12)
        ]
        assert codes[:10] == [401] * 10
        assert 429 in codes


class TestCORSAndSettings:
    def test_cors_not_open_to_arbitrary_origin(self, api_client, db):
        r = api_client.get('/api/health/', HTTP_ORIGIN='https://evil.example')
        assert 'Access-Control-Allow-Origin' not in r

    def test_cors_allows_configured_origin(self, api_client, db):
        r = api_client.get('/api/health/', HTTP_ORIGIN='http://localhost:5173')
        assert r['Access-Control-Allow-Origin'] == 'http://localhost:5173'
        assert 'Access-Control-Allow-Credentials' not in r

    def test_secret_key_required_in_production(self, monkeypatch):
        """Settings must refuse to start without SECRET_KEY when DEBUG is off."""
        import importlib
        import sys
        from django.core.exceptions import ImproperlyConfigured
        monkeypatch.delenv('SECRET_KEY', raising=False)
        monkeypatch.delenv('DEBUG', raising=False)
        monkeypatch.setattr('dotenv.load_dotenv', lambda *a, **k: None)  # ignore a developer's local .env
        monkeypatch.delitem(sys.modules, 'pytest')  # TESTING is detected via sys.modules
        monkeypatch.setattr(sys, 'argv', ['gunicorn'])
        mod = importlib.import_module('chemviz_backend.settings')
        try:
            with pytest.raises(ImproperlyConfigured):
                importlib.reload(mod)
        finally:
            sys.modules['pytest'] = pytest
            importlib.reload(mod)

    def test_api_auth_session_login_not_exposed(self, api_client, db):
        assert api_client.get('/api-auth/login/').status_code == 404
