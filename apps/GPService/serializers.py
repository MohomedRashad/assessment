from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability
from rest_framework.response import Response

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        exclude = ('doctor', 'is_booked')

    def validate(self, data):
        instance = Availability(**data)
        instance.clean()
        return data
