from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability, Appointment
from rest_framework.response import Response

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        exclude = ('doctor', 'is_booked')

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        exclude = ('patient', 'status')

