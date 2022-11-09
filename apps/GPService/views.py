from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import AvailabilitySerializer
from .models import Availability
from datetime import datetime

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.is_booked == False:
            serializer.save()
        else:
            return


    def perform_destroy(self, instance):
        availability = self.get_object()
        if availability.doctor != self.request.user:
            return
        elif availability.is_booked == True:
            return
        else:
            instance.delete()
