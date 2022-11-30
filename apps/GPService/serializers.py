from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability, Appointment, FormAssessmentQuestion

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        exclude = ('doctor',)

class AppointmentSerializer(serializers.ModelSerializer):
    availability = AvailabilitySerializer(read_only=True)
    class Meta:
        model = Appointment
        exclude = ('patient',)

class AddAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        exclude = ('patient', 'status')

class UpbateAppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status']

class FormAssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessmentQuestion
        fields = '__all__'

