from rest_framework import viewsets, status
from apps.horarios.models import Horario
from apps.horarios.serializers import HorarioSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all().order_by('-fecha_subida')
    serializer_class = HorarioSerializer

    @action(detail=False, methods=['post'])
    def limpiar_archivos(self, request):
        """Endpoint para forzar la limpieza de archivos huérfanos"""
        Horario.limpiar_archivos_huerfanos()
        return Response({"message": "Limpieza completada"})

    def perform_create(self, serializer):
        instance = serializer.save()
        # No llamar a limpiar_archivos_huerfanos aquí

    def perform_update(self, serializer):
        instance = serializer.save()
        # No llamar a limpiar_archivos_huerfanos aquí

    def perform_destroy(self, instance):
        instance.delete()
        # No llamar a limpiar_archivos_huerfanos aquí