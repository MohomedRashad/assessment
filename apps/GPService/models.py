import datetime
from enum import unique
from django.utils.translation import gettext_lazy as _
from secrets import choice
from unittest.util import _MAX_LENGTH
from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.files.models import File

class Availability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    starting_time = models.TimeField(default=timezone.now)
    ending_time = models.TimeField(default=timezone.now)
    is_booked = models.BooleanField(default=False)
    doctor_charge = models.IntegerField(default=1000)

class AppointmentStatus(models.TextChoices):
    BOOKED = 'BOOKED', _('BOOKED')
    ONGOING = 'ONGOING', _('ONGOING')
    COMPLETED = 'COMPLETED', _('COMPLETED')
    CANCELED = 'CANCELED', _('CANCELED')

class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=15,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.BOOKED   
        )
    attachment = models.FilePathField(null=True, blank=True)

class MedicineType(models.TextChoices):
    TABLET = 'TABLET', _('TABLET')
    CAPSULES = 'CAPSULES', _('CAPSULES')
    VACCINE = 'VACCINE', _('VACCINE')

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(
        max_length=50,
        choices=MedicineType.choices,
        )
    available_quantity = models.IntegerField()
    price = models.DecimalField(max_digits=4, decimal_places=2)

class AvailableTreatment(models.TextChoices):
    CANCER = 'CANCER', _('CANCER')
    ALLERGIES = 'ALLERGIES', _('ALLERGIES')

class FormAssessmentQuestion(models.Model):
    treatment = models.CharField(
        max_length=100,
        choices=AvailableTreatment.choices
        )
    question_title = models.CharField(max_length=200)

class FormAssessmentType(models.TextChoices):
    ONETIMEFORM = 'ONETIMEFORM', _('ONETIMEFORM')
    SUBSCRIPTIONFORM = 'SUBSCRIPTIONFORM', _('SUBSCRIPTIONFORM')

class FormAssessment(models.Model):
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='formassessments',
        blank=True,
        null=True
        )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True
        )
    type = models.CharField(
        max_length=20,
choices=FormAssessmentType.choices
    )
    is_assessed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    assessed_date = models.DateTimeField(null=True)

class FormAssessmentAnswer(models.Model):
    form_assessment_question = models.ForeignKey(FormAssessmentQuestion, on_delete=models.CASCADE)
    form_assessment = models.ForeignKey(FormAssessment, on_delete=models.CASCADE)
    answer = models.TextField()

class FormAssessmentFeedback(models.Model):
    form_assessment = models.ForeignKey(FormAssessment, on_delete=models.CASCADE)
    provided_feedback = models.TextField()
    posted_date = models.DateField(timezone.now)

class Prescription(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    prescribed_quantity = models.IntegerField()
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        blank=True,
        null=True
        )
    form_assessment = models.ForeignKey(
        FormAssessment,
        on_delete=models.CASCADE,
        blank=True,
        null=True
        )
    is_accepted = models.BooleanField(default=False)

class OrderType(models.TextChoices):
    FORMASSESSMENT = 'FORMASSESSMENT', _('FORMASSESSMENT')
    VIDEOASSESSMENT = 'VIDEOASSESSMENT', _('VIDEOASSESSMENT')
    PRESCRIPTION = 'PRESCRIPTION', _('PRESCRIPTION')

class Order(models.Model):
    type = models.CharField(
        max_length=50,
        choices=OrderType.choices)
    appointment = models.ForeignKey(Appointment,
    on_delete=models.CASCADE,
    null=True
    )
    form_assessment = models.ForeignKey(FormAssessment,   
    on_delete=models.CASCADE,
    null=True
    )
    created_date = models.DateTimeField(timezone.now)
total_amount = models.IntegerField(blank=True, null=True)

class Country(models.Model):
    name = models.CharField(max_length=50)

class RecommendedVaccine(models.Model)    :
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    Medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    posted_date = models.DateTimeField(timezone.now)
