from rest_framework.permissions import BasePermission
from profiles.choices import Role


class IsAdminUser(BasePermission):
    """
    Custom permission to allow access only to admin users.

    The user must be:
    - Authenticated
    - Role 'ADMIN'
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.ADMIN


class IsAdminOrGuestUser(BasePermission):
    """
    Custom permission to allow access to both admin and guest users.

    The user must be:
    - Authenticated
    - Role either 'ADMIN' or 'GUEST'
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Role.ADMIN, Role.GUEST]
