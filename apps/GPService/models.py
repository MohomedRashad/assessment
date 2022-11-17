import datetime
from datetime import date
from django.core.validators import MinValueValidator
from enum import unique
from django.utils.translation import gettext_lazy as _
from secrets import choice
from unittest.util import _MAX_LENGTH
from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.files.models import File
from rest_framework.exceptions import ValidationError

# TextChoices
class AppointmentStatus(models.TextChoices):
    BOOKED = 'BOOKED', _('BOOKED')
    ONGOING = 'ONGOING', _('ONGOING')
    COMPLETED = 'COMPLETED', _('COMPLETED')
    CANCELED = 'CANCELED', _('CANCELED')


class MedicineType(models.TextChoices):
    TABLET = 'TABLET', _('TABLET')
    CAPSULES = 'CAPSULES', _('CAPSULES')
    VACCINE = 'VACCINE', _('VACCINE')


class Treatment(models.TextChoices):
    CANCER = 'CANCER', _('CANCER')
    ALLERGIES = 'ALLERGIES', _('ALLERGIES')


class FormAssessmentType(models.TextChoices):
    ONE_TIME_FORM = 'ONE_TIME_FORM', _('ONE_TIME_FORM')
    SUBSCRIPTION_FORM = 'SUBSCRIPTION_FORM', _('SUBSCRIPTION_FORM')


class OrderType(models.TextChoices):
    FORM_ASSESSMENT = 'FORM_ASSESSMENT', _('FORM_ASSESSMENT')
    VIDEO_ASSESSMENT = 'VIDEO_ASSESSMENT', _('VIDEO_ASSESSMENT')
    PRESCRIPTION = 'PRESCRIPTION', _('PRESCRIPTION')


#Models
class Availability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField(
        default=timezone.now,
        validators=[MinValueValidator(limit_value=date.today)]
        )
    starting_time = models.TimeField()
    ending_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    doctor_charge = models.PositiveIntegerField(default=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['starting_time', 'ending_time', 'doctor'],
                name = 'unique_appointment_slot'
            )
        ]

    def clean(self):
        if self.starting_time > self.ending_time:
            raise ValidationError("The starting time should not be less than the ending time")

class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='appointments')
    status = models.CharField(
        max_length=15,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.BOOKED   
        )
    attachment = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(
        max_length=50,
        choices=MedicineType.choices,
        )
    available_quantity = models.IntegerField()
    price = models.DecimalField(max_digits=4, decimal_places=2)

class FormAssessmentQuestion(models.Model):
    treatment = models.CharField(
        max_length=100,
        choices=Treatment.choices
        )
    question = models.CharField(max_length=200)

class FormAssessment(models.Model):
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_formassessments',
        blank=True,
        null=True
        )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='doctor_formassessments'
        )
    type = models.CharField(
        max_length=20,
choices=FormAssessmentType.choices
    )
    is_assessed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    assessed_date = models.DateTimeField(null=True)

class FormAssessmentAnswer(models.Model):
    form_assessment_question = models.ForeignKey(FormAssessmentQuestion, on_delete=models.CASCADE, related_name='form_assessment_answers')
    form_assessment = models.ForeignKey(FormAssessment, on_delete=models.CASCADE, related_name='form_assessment_answers')
    answer = models.TextField()

class FormAssessmentFeedback(models.Model):
    form_assessment = models.ForeignKey(FormAssessment, on_delete=models.CASCADE, related_name='form_assessment_feedback')
    provided_feedback = models.TextField()
    posted_date = models.DateField(timezone.now)

class Prescription(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='prescriptions')
    prescribed_quantity = models.IntegerField()
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='prescriptions'
        )
    form_assessment = models.ForeignKey(
        FormAssessment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='prescriptions'
        )
    is_accepted = models.BooleanField(default=False)

class Order(models.Model):
    type = models.CharField(
        max_length=50,
        choices=OrderType.choices)
    appointment = models.ForeignKey(Appointment,
    on_delete=models.CASCADE,
    null=True,
    related_name='orders'
    )
    form_assessment = models.ForeignKey(FormAssessment,   
    on_delete=models.CASCADE,
    null=True,
    related_name='orders'
    )
    created_date = models.DateTimeField(timezone.now)
    total_amount = models.IntegerField(blank=True, null=True)

class Country(models.Model):
    name = models.CharField(max_length=50)

class RecommendedVaccine(models.Model)    :
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='recommended_vaccines')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, blank=True, null=True, related_name='recommended_vaccines')
    posted_date = models.DateTimeField(timezone.now)
