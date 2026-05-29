import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import CustomUser
from apps.accounts.enums import Role


class AdminFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f'admin{n}@test.com')
    first_name = 'Admin'
    last_name = factory.Sequence(lambda n: f'User{n}')
    role = Role.ADMIN
    is_staff = True
    is_superuser = True
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class DeanFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f'dean{n}@test.com')
    first_name = 'Dean'
    last_name = factory.Sequence(lambda n: f'User{n}')
    role = Role.DEAN
    faculty = None
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class SupervisorFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f'supervisor{n}@test.com')
    first_name = 'Supervisor'
    last_name = factory.Sequence(lambda n: f'User{n}')
    role = Role.SUPERVISOR
    faculty = None
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class StudentFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f'student{n}@test.com')
    first_name = 'Student'
    last_name = factory.Sequence(lambda n: f'User{n}')
    role = Role.STUDENT
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
