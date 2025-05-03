from rest_framework import viewsets
from apps.biblioteca.models import Libro
from apps.biblioteca.serializers import LibroSerializer

class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all().order_by('-fecha_subida')
    serializer_class = LibroSerializer