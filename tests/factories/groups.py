import factory
from factory.django import DjangoModelFactory

from apps.institutions.models import Faculty, Department
from apps.groups.models import ProjectGroup, GroupMembership
from .users import SupervisorFactory, StudentFactory


class FacultyFactory(DjangoModelFactory):
    class Meta:
        model = Faculty

    name = factory.Sequence(lambda n: f'Faculty of Science {n}')
    code = factory.Sequence(lambda n: f'FS{n}')


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f'Department {n}')
    code = factory.Sequence(lambda n: f'D{n}')
    faculty = factory.SubFactory(FacultyFactory)


class ProjectGroupFactory(DjangoModelFactory):
    class Meta:
        model = ProjectGroup

    name = factory.Sequence(lambda n: f'Group {n}')
    supervisor = factory.SubFactory(SupervisorFactory)
    department = factory.SubFactory(DepartmentFactory)
    academic_year = '2025/2026'


class GroupMembershipFactory(DjangoModelFactory):
    class Meta:
        model = GroupMembership

    group = factory.SubFactory(ProjectGroupFactory)
    student = factory.SubFactory(StudentFactory)
