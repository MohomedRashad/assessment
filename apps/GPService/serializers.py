from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Availability, Appointment, FormAssessmentQuestion, FormAssessment, FormAssessmentAnswer, FormAssessmentFeedback, Medicine, Treatment, Country, RecommendedVaccine, Prescription

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

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class ViewRecommendedVaccineSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    medicine = MedicineSerializer()
    class Meta:
        model = RecommendedVaccine
        fields = '__all__'

class AddRecommendedVaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedVaccine
        fields = '__all__'

class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = ['name']

class FormAssessmentQuestionSerializer(serializers.ModelSerializer):
    treatments = TreatmentSerializer(read_only=True, many=True)
    class Meta:
        model = FormAssessmentQuestion
        fields = ('id', 'treatments', 'question')

class ViewAllFormAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessment
        exclude = ('patient',)

class ViewFormAssessmentSerializer(serializers.ModelSerializer):
    form_assessment_answers = serializers.SerializerMethodField()
    class Meta:
        model = FormAssessment
        fields = ('id', 'form_assessment_answers', 'doctor', 'type', 'is_assessed', 'created_date', 'assessed_date')

    def get_form_assessment_answers(self, instance):
        # get the form assessment answers for the given form assessment instance
        queryset = FormAssessmentAnswer.objects.filter(form_assessment = instance.id)
        serializer = ViewFormAssessmentAnswerSerializer(queryset, many=True)
        return serializer.data
        
class ViewFormAssessmentAnswerSerializer(serializers.ModelSerializer):
    form_assessment_question = FormAssessmentQuestionSerializer()
    class Meta:
        model = FormAssessmentAnswer
        fields = ('id', 'form_assessment_question', 'answer')

class AddFormAssessmentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessmentAnswer
        fields = '__all__'

class ViewFormAssessmentFeedbackSerializer(serializers.ModelSerializer):
    form_assessment = ViewAllFormAssessmentSerializer()
    class Meta:
        model = FormAssessmentFeedback
        fields = '__all__'

class AddFormAssessmentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAssessmentFeedback
        fields = '__all__'

class ViewPrescriptionSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer(many=True)
    class Meta:
        model = Prescription
        fields = '__all__'

class AddPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'
