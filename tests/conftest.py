import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories.users import AdminFactory, DeanFactory, SupervisorFactory, StudentFactory
from tests.factories.groups import FacultyFactory, DepartmentFactory, ProjectGroupFactory, GroupMembershipFactory


def _auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client, user


@pytest.fixture
def admin_client(db):
    return _auth_client(AdminFactory())


@pytest.fixture
def faculty(db):
    return FacultyFactory()


@pytest.fixture
def department(db, faculty):
    return DepartmentFactory(faculty=faculty)


@pytest.fixture
def dean(db, faculty):
    return DeanFactory(faculty=faculty)


@pytest.fixture
def dean_client(db, faculty):
    d = DeanFactory(faculty=faculty)
    return _auth_client(d)


@pytest.fixture
def supervisor(db, faculty):
    s = SupervisorFactory(faculty=faculty)
    return s


@pytest.fixture
def supervisor_client(db, faculty):
    s = SupervisorFactory(faculty=faculty)
    return _auth_client(s)


@pytest.fixture
def student(db):
    return StudentFactory()


@pytest.fixture
def student_client(db):
    s = StudentFactory()
    return _auth_client(s)


@pytest.fixture
def project_group(db, supervisor, department):
    return ProjectGroupFactory(supervisor=supervisor, department=department)


@pytest.fixture
def group_with_student(db, project_group, student):
    GroupMembershipFactory(group=project_group, student=student)
    return project_group, student
