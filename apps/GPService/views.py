from rest_framework import viewsets
from django.http import Http404
from rest_framework import status
from .models import Availability, Appointment, Medicine, Country, RecommendedVaccine
from .serializers import AvailabilitySerializer, AppointmentSerializer, AddAppointmentSerializer, UpbateAppointmentStatusSerializer, MedicineSerializer, CountrySerializer, ViewRecommendedVaccineSerializer, AddRecommendedVaccineSerializer
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
        starting_time = datetime.strptime(self.request.data.get('starting_time'), '%H:%M:%S')
        ending_time = datetime.strptime(self.request.data.get('ending_time'), '%H:%M:%S')
        if availability.is_booked:
            raise ValidationError("This availability instance cannot be modified as it has already been booked before")            
        elif Availability.objects.filter(
            date=self.request.data['date'],
            starting_time=self.request.data['starting_time'],
            ending_time=self.request.data['ending_time'],
            doctor=self.request.user).exists():
            raise ValidationError("This availability instance has already been added before")
        elif not check_meeting_slot_time(
            starting_time.time(),
            ending_time.time()):
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
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'destroy':
            return UpbateAppointmentStatusSerializer
        elif self.action == 'create':
            return AddAppointmentSerializer
        return super(AppointmentViewSet, self).get_serializer_class()

    def get_queryset(self):
        status = self.request.query_params.get('status')
        if status is not None:
            self.queryset.filter(status=status, patient=self.request.user)
        else:
            self.queryset.filter(patient=self.request.user)
        return self.queryset

    @transaction.atomic
    def perform_create(self, serializer):
        availability = get_object_or_404(
            Availability, id = self.request.data.get('availability'))
        if Appointment.objects.filter(
            patient=self.request.user,
            availability=self.request.data.get('availability')).exclude(
            status='CANCELED').exists():
            raise ValidationError("This appointment has already been added before")
        else:
            #Adding the appointment
            serializer.save(patient=self.request.user)
            #Updating the chosen availability status to booked.
            availability.is_booked = True
            availability.save()

    @transaction.atomic
    def perform_update(self, serializer):
        appointment = self.get_object()
        if not 'status' in self.request.data:
            raise ValidationError("The status has not been provided")
        elif appointment.status == 'COMPLETED':
            raise ValidationError("This appointment cannot be modified as it has already been completed")
        elif self.request.data['status'] == 'CANCELED':
            #An appointment can be deleted only if the current status is set to 'BOOKED'
            if appointment.status == 'ONGOING':
                raise ValidationError("This appointment cannot be deleted, as it is ongoing at the moment")
            else:
                    #Updating the availability status to not booked.
                    availability = get_object_or_404(
                        Availability, id = appointment.availability.id)
                    availability.is_booked = False
                    availability.save()
                        #Setting the appointment status to 'CANCELED'
                    super().perform_update(serializer)
        else:
            super().perform_update(serializer)

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer

class RecommendedVaccineViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            return AddRecommendedVaccineSerializer
        elif self.request.query_params.get('country'):
            return ViewRecommendedVaccineSerializer
        return super(RecommendedVaccineViewSet, self).get_serializer_class()

    def get_queryset(self):
        country = self.request.query_params.get('country')
        if country is not None:
            #return RecommendedVaccine.objects.all()
            return RecommendedVaccine.objects.filter(country__name__startswith=country)
        return self.queryset
