from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import Roles

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class UpdateOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method == 'PUT'


class AnonWriteOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method == 'POST'


class IsManager(BasePermission):
    def has_permission(self, request, view):
        if request.user is not None and\
                hasattr(request.user, 'profile') and \
                request.user.profile.role.id == 1:
            return True
        return False


class IsCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, 'profile'):
            return request.user.profile.company.id == int(view.kwargs.get("pk"))
        return False


class HasResourcePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin_user()


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_super_admin()


class NotAllowed(BasePermission):
    def has_permission(self, request, view):
        raise PermissionDenied()

class DoctorOrReadOnly(BasePermission):
    """
    Custom permission to only allow doctors to edit their availability.
    """

    def has_permission(self, request, view):
        # Allow all authenticated users to view doctor availabilities
        if request.method in SAFE_METHODS:
            return True

        # Only allow doctors to create availabilities
        return request.user.role == Roles.DOCTOR

    def has_object_permission(self, request, view, obj):
        # Allow all authenticated users to view doctor availabilities
        if request.method in SAFE_METHODS:
            return True

        # Only allow the specific doctor to update or delete their own availability
        return obj.doctor == request.user

class SystemAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins of the system to add and edit medicines.
    """

    def has_permission(self, request, view):
        # Allow all authenticated users to view medicines
        if request.method in SAFE_METHODS:
            return True

        # Allow superusers to perform non-safe methods
        if request.user.role == Roles.SUPER_ADMIN:
            return True

    def has_object_permission(self, request, view, obj):
        # Allow all authenticated users to view m   edicines
        if request.method in SAFE_METHODS:
            return True

        # Allow superusers to edit the medicine instance
        if request.user.role == Roles.SUPER_ADMIN:
            return True
