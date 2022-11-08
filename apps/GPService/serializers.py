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

    def validate(self, data):
        if data['starting_time'] > data['ending_time']:
            raise serializers.ValidationError("The starting time should not be greater than the ending time")
        elif Availability.objects.filter(
            date=data['date'],
            starting_time=data['starting_time'],
            ending_time=data['ending_time']):
            raise serializers.ValidationError("This availability instance has already been added before")

        return data