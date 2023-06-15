import uuid
import datetime
from datetime import date
from django.core.validators import MinValueValidator
from enum import unique
from django.utils.translation import gettext_lazy as _
from secrets import choice
from unittest.util import _MAX_LENGTH
from django.db import models
from django.utils import timezone
from django.db.models import Q
from apps.users.models import Doctor, Pharmacy, User, Patient
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

class FormAssessmentType(models.TextChoices):
    ONE_TIME_FORM = 'ONE_TIME_FORM', _('ONE_TIME_FORM')
    SUBSCRIPTION_FORM = 'SUBSCRIPTION_FORM', _('SUBSCRIPTION_FORM')

class OrderType(models.TextChoices):
    FORM_ASSESSMENT = 'FORM_ASSESSMENT', _('FORM_ASSESSMENT')
    VIDEO_ASSESSMENT = 'VIDEO_ASSESSMENT', _('VIDEO_ASSESSMENT')

class PharmacyReviewStatus(models.TextChoices):
    ACCEPTED = 'ACCEPTED', _('ACCEPTED')
    REJECTED = 'REJECTED', _('REJECTED')
    PENDING = 'PENDING', _('PENDING')

#Models
class Availability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
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
                fields = ['date', 'starting_time', 'ending_time', 'doctor'],
                name = 'unique_appointment_slot'
            )
                    ]

    def save(self, *args, **kwargs):
        if  self.ending_time < self.starting_time:
            raise ValidationError("The ending time should not be less than the starting time")
        else:
                            super().save(*args, **kwargs)

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='appointments')
    status = models.CharField(
        max_length=15,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.BOOKED   
        )
    attachment = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['patient', 'availability'],
                condition = ~Q(status='CANCELED'),
                name = 'unique_appointment'
            )
                    ]

class Medicine(models.Model):
    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(
        max_length=50,
        choices=MedicineType.choices,
        )
    available_quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])

class Treatment(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class FormAssessmentQuestion(models.Model):
    treatments = models.ManyToManyField(Treatment)
    question = models.CharField(max_length=200)

    def __str__(self):
        return self.question

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

    def __str__(self):
        return self.answer

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['form_assessment_question', 'form_assessment'], name='unique_answer_per_question_per_form')
        ]

class FormAssessmentFeedback(models.Model):
    form_assessment = models.ForeignKey(
        FormAssessment,
        on_delete=models.CASCADE,
        related_name='form_assessment_feedback'
        )
    provided_feedback = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.provided_feedback

class Prescription(models.Model):
    medicines = models.ManyToManyField(Medicine, related_name='prescriptions')
    prescribed_quantity = models.PositiveIntegerField()
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='prescription'
        )
    form_assessment = models.OneToOneField(
        FormAssessment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='prescription'
        )
    description = models.TextField(blank=True, null=True)
    is_accepted = models.BooleanField(default=False)
    pharmacy = models.OneToOneField(
        Pharmacy,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='prescription'
        )
    pharmacy_review_status = models.CharField(
        max_length=15,
        choices = PharmacyReviewStatus.choices,
        default= PharmacyReviewStatus.PENDING
        )
    reason_for_rejection = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check = models.Q(appointment__isnull=True) | models.Q(form_assessment__isnull = True),
                name='one_record_constraint'
            )
        ]


class Order(models.Model):
    type = models.CharField(
        max_length=50,
        choices=OrderType.choices)
    appointment = models.OneToOneField(Appointment,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='order'
    )
    form_assessment = models.OneToOneField(FormAssessment,   
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='order'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.PositiveIntegerField(blank=True, null=True)

class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)

class RecommendedVaccine(models.Model)    :
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='recommended_vaccines')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, blank=True, null=True, related_name='recommended_vaccines')
    posted_date = models.DateTimeField(auto_now_add=True)
