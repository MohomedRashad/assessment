from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability, Appointment

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        exclude = ('doctor', 'is_booked')

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        exclude = ('patient', 'status')

    def update(self, instance, validated_data):
                    instance.status = validated_data.get('status')
                    instance.save()
                    return instance