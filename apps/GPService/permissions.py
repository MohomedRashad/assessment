from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import Roles

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