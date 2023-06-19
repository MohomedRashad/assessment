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

class DoctorWriteOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS and request.user.role != Roles.PHARMACY:
            return True

        return request.user.role == Roles.DOCTOR

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS and request.user.role != Roles.PHARMACY:
            return True

        return obj.doctor == request.user.doctor

class PharmacyOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user

class SystemAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user.role == Roles.SUPER_ADMIN:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.user.role == Roles.SUPER_ADMIN:
            return True

class PatientWriteOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS and request.user.role != Roles.PHARMACY:
            return True

        return request.user.role == Roles.PATIENT

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS and request.user.role != Roles.PHARMACY:
            return True

        return obj.patient == request.user.patient

class IsAllowedToAccessAssessment(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == Roles.DOCTOR:
            if obj.doctor is not None and obj.doctor != request.user:
                return False
        elif request.user.role == Roles.PATIENT:
            if obj.patient != request.user:
                return False
        return True
