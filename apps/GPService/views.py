from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import AvailabilitySerializer
from .models import Availability
from datetime import datetime
from rest_framework.exceptions import ValidationError
from apps.common.services import is_the_appointment_slot_exactly_15_minutes

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer


    def perform_create(self, serializer):
        if Availability.objects.filter(
            date=serializer.validated_data['date'],
            starting_time=serializer.validated_data['starting_time'],
            ending_time=serializer.validated_data['ending_time'],
            doctor=self.request.user):
            raise ValidationError("This availability instance has already been added before")
        elif not is_the_appointment_slot_exactly_15_minutes(
            serializer.validated_data['starting_time'],
            serializer.validated_data['ending_time']):
            raise ValidationError("The duration of the availability slot should exactly be 15 minutes")
        else:
            serializer.save(doctor=self.request.user)


    def perform_update(self, serializer):
        availability = self.get_object()
        if availability.is_booked:
            raise ValidationError("This availability instance cannot be modified as it has already been booked before")            
        elif Availability.objects.filter(
            date=availability.date,
            starting_time=availability.starting_time,
            ending_time=availability.ending_time,
            doctor=self.request.user):
            raise ValidationError("This availability instance has already been added before")
        elif not is_the_appointment_slot_exactly_15_minutes(
            availability.starting_time,
            availability.ending_time):
            raise ValidationError("The duration of the availability slot should exactly be 15 minutes")
        else:
            super().perform_update(serializer)


    def perform_destroy(self, instance):
        availability = self.get_object()
        if availability.doctor != self.request.user:
            raise ValidationError("You are not authorized to delete this availability instance")
        elif availability.is_booked:
            raise ValidationError("This availability instance cannot be deleted as it has been associated with an appointment")
        else:
            super().perform_destroy(instance)
