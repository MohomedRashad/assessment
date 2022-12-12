from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Availability, Appointment, Medicine, Country, RecommendedVaccine

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

