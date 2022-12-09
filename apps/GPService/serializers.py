from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability, Appointment, FormAssessmentQuestion, FormAssessment, FormAssessmentAnswer, FormAssessmentFeedback, Medicine, Treatment

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

class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = ['name']

class FormAssessmentQuestionSerializer(serializers.ModelSerializer):
    treatments = TreatmentSerializer(read_only=True, many=True)
    class Meta:
        model = FormAssessmentQuestion
        fields = '__all__'

class ViewFormAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessment
        exclude = ('patient',)

class FormAssessmentAnswerSerializer(serializers.ModelSerializer):
    form_assessment = ViewFormAssessmentSerializer(read_only=True)
    form_assessment_question = FormAssessmentQuestionSerializer(read_only=True)
    class Meta:
        model = FormAssessmentAnswer
        fields = '__all__'

class FormAssessmentFeedbackSerializer(serializers.ModelSerializer):
    form_assessment = ViewFormAssessmentSerializer(read_only=True)
    class Meta:
        model = FormAssessmentFeedback
        fields = '__all__'

