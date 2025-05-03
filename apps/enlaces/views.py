from rest_framework import viewsets
from apps.enlaces.models import EnlaceClaseGrabada, EnlaceCurso
from apps.enlaces.serializers import EnlaceClaseGrabadaSerializer, EnlaceCursoSerializer

class EnlaceClaseGrabadaViewSet(viewsets.ModelViewSet):
    queryset = EnlaceClaseGrabada.objects.all()
    serializer_class = EnlaceClaseGrabadaSerializer

    def get_queryset(self):
        queryset = EnlaceClaseGrabada.objects.all()
        salon = self.request.query_params.get('salon', None)
        if salon is not None:
            queryset = queryset.filter(salon=salon)
        return queryset

class EnlaceCursoViewSet(viewsets.ModelViewSet):
    queryset = EnlaceCurso.objects.all()
    serializer_class = EnlaceCursoSerializer

    def get_queryset(self):
        queryset = EnlaceCurso.objects.all()
        salon = self.request.query_params.get('salon', None)
        if salon is not None:
            queryset = queryset.filter(salon=salon)
        return queryset
