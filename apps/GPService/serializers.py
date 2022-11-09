from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability
from rest_framework.response import Response
from datetime import datetime

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
        #validating the availability slots to be exactly 15 minutes
        start_time = datetime.strptime(data['starting_time'].isoformat(), "%H:%M:%S")
        end_time = datetime.strptime(data['ending_time'].isoformat(), "%H:%M:%S")
        delta = end_time - start_time
        sec = delta.total_seconds()
        min = sec / 60

        #Validations
        if data['starting_time'] > data['ending_time']:
            raise serializers.ValidationError("The starting time should not be greater than the ending time")
        elif Availability.objects.filter(
            date=data['date'],
            starting_time=data['starting_time'],
            ending_time=data['ending_time'],
            doctor=self.context['request'].user):
            raise serializers.ValidationError("This availability instance has already been added before")
        elif min != 15:
                raise serializers.ValidationError("The duration of the availability slot should exactly be 15 minutes")

        return data
