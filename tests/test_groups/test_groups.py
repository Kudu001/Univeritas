import pytest
from apps.groups.models import GroupMembership


@pytest.mark.django_db
class TestCreateGroup:
    url = '/api/v1/groups/'

    def test_supervisor_can_create_group(self, supervisor_client, department):
        client, supervisor = supervisor_client
        resp = client.post(self.url, {
            'name': 'Alpha Group',
            'department_id': str(department.id),
            'academic_year': '2025/2026',
        })
        assert resp.status_code == 201
        assert resp.data['data']['name'] == 'Alpha Group'

    def test_invalid_academic_year_format_fails(self, supervisor_client, department):
        client, _ = supervisor_client
        resp = client.post(self.url, {
            'name': 'Beta', 'department_id': str(department.id), 'academic_year': '2025-2026',
        })
        assert resp.status_code == 400

    def test_student_cannot_create_group(self, student_client, department):
        client, _ = student_client
        resp = client.post(self.url, {
            'name': 'Gamma', 'department_id': str(department.id), 'academic_year': '2025/2026',
        })
        assert resp.status_code == 403


@pytest.mark.django_db
class TestAddMember:
    def test_cannot_add_more_than_3_members(self, supervisor_client, project_group):
        from tests.factories.users import StudentFactory
        client, _ = supervisor_client
        url = f'/api/v1/groups/{project_group.id}/members/'

        # Fill group to max
        for i in range(3):
            client.post(url, {
                'first_name': 'S', 'last_name': str(i), 'email': f's{i}_x@test.com',
            })

        # 4th should fail
        resp = client.post(url, {'first_name': 'X', 'last_name': 'Y', 'email': 'fourth@test.com'})
        assert resp.status_code == 422
