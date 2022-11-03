from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ('id', 'date', 'starting_time', 'ending_time', 'is_booked', 'doctor_charge')
        extra_kwargs = {
            'id': {'read_only': True},
            'date': {'required': True},
            'starting_time': {'required': True},
            'ending_time': {'required': True},
            'is_booked': {'required': True},
            'doctor_charge': {'required': True},
        }
        ordering = ['-date']
