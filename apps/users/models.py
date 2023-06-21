from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

import uuid

from safedelete.models import SafeDeleteModel

from apps.common.email_templates import EmailTemplates
from apps.common.services import generate_token, send_mail


class Roles(models.TextChoices):
    # User Roles
    SUPER_ADMIN = 'SUPER_ADMIN', _('SUPER_ADMIN')
    ADMIN = 'ADMIN', _('ADMIN')
    DOCTOR = 'DOCTOR', _('DOCTOR')
    PATIENT = 'PATIENT', _('PATIENT')
    PHARMACY = 'PHARMACY', _('PHARMACY')

class User(AbstractUser, SafeDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.PATIENT
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def is_super_admin(self):
        return self.role == Roles.SUPER_ADMIN or self.is_superuser

    def is_admin_user(self):
        return self.role in [Roles.ADMIN, Roles.SUPER_ADMIN]

    def is_user(self):
        return self.role == Roles.USER

    def generate_email_verification_code(self):
        verification = self.email_verifications.create(code=generate_token(6))
        send_mail(
            'Please confirm your email.',
            self.email,
            EmailTemplates.AUTH_VERIFICATION,
            {'verification_code': verification.code}
        )

class UserEmailVerification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='email_verifications'
    )
    code = models.PositiveIntegerField()
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Pharmacy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacy')
    name = models.CharField(max_length = 100)
    address = models.TextField()
    phone = models.CharField(
        max_length=15,
        null=True,
        blank=True
        )
    postal_code = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    speciality = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    pharmacy = models.OneToOneField(Pharmacy, on_delete=models.CASCADE, related_name='pharmacy')

