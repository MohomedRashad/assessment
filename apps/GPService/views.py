from rest_framework import viewsets
from .serializers import AvailabilitySerializer
from .models import Availability

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer