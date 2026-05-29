import pytest
from tests.factories.groups import FacultyFactory
from tests.factories.users import AdminFactory, DeanFactory


@pytest.mark.django_db
class TestCreateDean:
    url = '/api/v1/accounts/deans/'

    def test_admin_can_create_dean(self, admin_client, faculty):
        client, _ = admin_client
        resp = client.post(self.url, {
            'first_name': 'Test',
            'last_name': 'Dean',
            'email': 'dean.new@test.com',
            'faculty_id': str(faculty.id),
        })
        assert resp.status_code == 201
        assert resp.data['data']['role'] == 'DEAN'

    def test_duplicate_dean_for_same_faculty_returns_409(self, admin_client, faculty):
        DeanFactory(faculty=faculty)
        client, _ = admin_client
        resp = client.post(self.url, {
            'first_name': 'Another',
            'last_name': 'Dean',
            'email': 'dean2@test.com',
            'faculty_id': str(faculty.id),
        })
        assert resp.status_code == 409

    def test_non_admin_cannot_create_dean(self, dean_client):
        client, _ = dean_client
        new_faculty = FacultyFactory()
        resp = client.post(self.url, {
            'first_name': 'X', 'last_name': 'Y',
            'email': 'x@test.com', 'faculty_id': str(new_faculty.id),
        })
        assert resp.status_code == 403


@pytest.mark.django_db
class TestCreateSupervisor:
    url = '/api/v1/accounts/supervisors/'

    def test_dean_can_create_supervisor(self, dean_client):
        client, _ = dean_client
        resp = client.post(self.url, {
            'first_name': 'Super', 'last_name': 'Visor', 'email': 'sv@test.com',
        })
        assert resp.status_code == 201
        assert resp.data['data']['role'] == 'SUPERVISOR'

    def test_admin_cannot_create_supervisor(self, admin_client):
        client, _ = admin_client
        resp = client.post(self.url, {
            'first_name': 'X', 'last_name': 'Y', 'email': 'xy@test.com',
        })
        assert resp.status_code == 403
