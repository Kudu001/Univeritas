import pytest
from rest_framework.test import APIClient
from tests.factories.users import AdminFactory


@pytest.mark.django_db
class TestLogin:
    url = '/api/v1/auth/login/'

    def test_valid_credentials_return_tokens(self):
        user = AdminFactory()
        client = APIClient()
        resp = client.post(self.url, {'email': user.email, 'password': 'testpass123'})
        assert resp.status_code == 200
        assert resp.data['status'] == 'success'
        assert 'access' in resp.data['data']
        assert 'refresh' in resp.data['data']

    def test_wrong_password_returns_400(self):
        user = AdminFactory()
        client = APIClient()
        resp = client.post(self.url, {'email': user.email, 'password': 'wrongpassword'})
        assert resp.status_code == 400
        assert resp.data['status'] == 'error'

    def test_unknown_email_returns_400(self):
        client = APIClient()
        resp = client.post(self.url, {'email': 'nobody@test.com', 'password': 'anything'})
        assert resp.status_code == 400

    def test_inactive_user_cannot_login(self):
        user = AdminFactory(is_active=False)
        client = APIClient()
        resp = client.post(self.url, {'email': user.email, 'password': 'testpass123'})
        assert resp.status_code == 400


@pytest.mark.django_db
class TestPasswordChange:
    url = '/api/v1/auth/password/change/'

    def test_change_password_sets_flag(self, admin_client):
        client, user = admin_client
        resp = client.post(self.url, {
            'current_password': 'testpass123',
            'new_password': 'NewSecure!99',
        })
        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.password_changed is True

    def test_wrong_current_password_fails(self, admin_client):
        client, _ = admin_client
        resp = client.post(self.url, {
            'current_password': 'wrongpass',
            'new_password': 'NewSecure!99',
        })
        assert resp.status_code == 400
