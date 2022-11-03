from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import AvailabilitySerializer
from .models import Availability

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

    def list(self, request, *args, **kwargs):
        queryset = Availability.objects.all()
        serializer = AvailabilitySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AvailabilitySerializer(instance=instance)
        return Response(serializer.data)

    def create(self, request):
        if request.user.is_authenticated and request.user.role == "DOCTOR":
            serializer = AvailabilitySerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(doctor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            #return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

