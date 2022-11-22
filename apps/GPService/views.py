from rest_framework import viewsets
from django.http import Http404
from rest_framework import status
from .models import Availability, Appointment
from apps.users.models import User
from .serializers import AvailabilitySerializer, AppointmentSerializer
from datetime import datetime
from rest_framework.exceptions import ValidationError
from .services import check_meeting_slot_time
from django.shortcuts import get_object_or_404
from django.db import transaction

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer


    def perform_create(self, serializer):
        starting_time = datetime.strptime(self.request.data.get('starting_time'), '%H:%M:%S')
        ending_time = datetime.strptime(self.request.data.get('ending_time'), '%H:%M:%S')
        if Availability.objects.filter(
            date=self.request.data.get('date'),
            starting_time=self.request.data.get('starting_time'),
            ending_time=self.request.data.get('ending_time'),
            doctor=self.request.user).exists():
            raise ValidationError("This availability instance has already been added before")
        elif not check_meeting_slot_time(
            starting_time.time(),
            ending_time.time()):
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
            doctor=self.request.user).exists():
            raise ValidationError("This availability instance has already been added before")
        elif not check_meeting_slot_time(
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

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        status = self.request.query_params.get('status')
        current_user = User.objects.get(id=self.request.user.id)
        if status is not None:
            queryset = current_user.appointments.all()
            queryset = queryset.filter(status=status)
        else:
            queryset = current_user.appointments.all()
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        availability = get_object_or_404(
            Availability, id = self.request.data.get('availability'))
        if Appointment.objects.filter(
            patient=self.request.user,
            availability=self.request.data.get('availability')).exists():
            raise ValidationError("This appointment has already been added before")
        else:
            #Adding the appointment
            serializer.save(patient=self.request.user)
            #Updating the chosen availability status to booked.
            availability.is_booked = True
            availability.save()

    def perform_update(self, serializer):
        appointment = self.get_object()
        if appointment.status == 'COMPLETED':
            raise ValidationError("This appointment cannot be modified as it has already been completed")
        else:
            serializer.save(status=self.request.data.get('status'))

    @transaction.atomic
    def perform_destroy(self, serializer):
        #An appointment can be deleted only if the current status is set to 'BOOKED'
        appointment = self.get_object()
        if appointment.status == 'COMPLETED':
            raise ValidationError("This appointment cannot be deleted, as it has been completed before")
        elif appointment.status == 'ONGOING':
            raise ValidationError("This appointment cannot be deleted, as it is ongoing at the moment")
        elif appointment.status == 'CANCELED':
            raise ValidationError("This appointment cannot be deleted, as it has already been canceled before")
        else:
            #Updating the availability status to not booked.
            availability = get_object_or_404(
                Availability, id = self.request.data.get('availability'))
            availability.is_booked = False
            availability.save()
                #Setting the appointment status to 'CANCELED'
            serializer.status = 'CANCELED'
            serializer.save()
