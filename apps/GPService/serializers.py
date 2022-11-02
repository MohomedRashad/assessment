from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ('id', 'doctor', 'date', 'starting_time', 'ending_time', 'is_booked', 'doctor_charge')
        ordering = ['-date']

