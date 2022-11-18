from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Availability, Appointment
from .serializers import AvailabilitySerializer, AppointmentSerializer
from datetime import datetime
from rest_framework.exceptions import ValidationError
from .services import check_meeting_slot_time

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
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        if Appointment.objects.filter(
            patient=self.request.user,
            availability=self.request.data.get('availability')).exists():
            raise ValidationError("This appointment has already been added before")
        else:
            #Updating the chosen availability status to booked.
            availability = Availability.objects.get(id=self.request.data.get('availability'))
            if availability:
                availability.is_booked = True
                availability.save()
                #Adding the appointment
                serializer.save(patient=self.request.user)

    def perform_update(self, serializer):
        appointment = self.get_object()
        if appointment.status == 'COMPLETED':
            raise ValidationError("This appointment cannot be modified as it has already been completed")
        elif not 'status' in self.request.data.keys():
                raise ValidationError("The status has not been provided")
        elif not self.request.data.get('status') == 'ONGOING' or not self.request.data.get('status') == 'COMPLETED':
            raise ValidationError("An invalid appointment status has been provided")
        else:
            serializer.save(status=self.request.data.get('status'))


    def perform_destroy(self, serializer):
        #An appointment can be deleted only if the current status is 'BOOKED'
        appointment = self.get_object()
        if appointment.status == 'COMPLETED':
            raise ValidationError("This appointment cannot be deleted, as it has been completed before")
        elif appointment.status == 'ONGOING':
            raise ValidationError("This appointment cannot be deleted, as it is ongoing at the moment")
        elif appointment.status == 'CANCELED':
            raise ValidationError("This appointment cannot be deleted, as it has already been canceled before")
        else:
            #Updating the availability status to not booked.
            availability = Availability.objects.get(id=self.request.data.get('availability'))
            if availability:
                availability.is_booked = False
                availability.save()
                #Setting the appointment status to 'CANCELED'
                serializer.status = 'CANCELED'
                serializer.save()

