from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability, Appointment, FormAssessmentQuestion, FormAssessment, FormAssessmentAnswer, FormAssessmentFeedback, Medicine

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

class UpdateAppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'status']

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class FormAssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessmentQuestion
        fields = '__all__'

class ViewFormAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessment
        exclude = ('patient',)

class AddFormAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessment
        exclude = ('patient', 'doctor', 'is_assessed', 'created_date', 'assessed_date',)

class UpdateFormAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessment
        exclude = ('patient', 'doctor', 'created_date', 'assessed_date', 'type',)

class FormAssessmentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessmentAnswer
        fields = '__all__'

class FormAssessmentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessmentFeedback
        exclude = ('posted_date',)
