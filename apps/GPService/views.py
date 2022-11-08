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

    def destroy(self, request, *args, **kwargs):
        availability = self.get_object()
        if availability.is_booked == False:
            availability.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response("Unable to delete this availability instance")