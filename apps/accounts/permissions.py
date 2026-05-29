from rest_framework.permissions import BasePermission
from .enums import Role


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.ADMIN


class IsDean(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.DEAN


class IsSupervisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.SUPERVISOR


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.STUDENT


class IsAdminOrDean(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (Role.ADMIN, Role.DEAN)


class IsDeanOrSupervisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (Role.DEAN, Role.SUPERVISOR)
