from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import date
from apps.membresias.models import Membresia  # Corregida la importación
from apps.asistencias.models import Asistencia
from apps.asistencias.serializers import AsistenciaSerializer
from apps.users.models import Usuario

class AsistenciaCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.rol not in ['admin', 'secretario']:
            return Response({'detail': 'No tienes permiso para registrar asistencias.'}, status=403)

        dni = request.data.get('dni')
        tipo = request.data.get('tipo', 'entrada')
        
        try:
            usuario = Usuario.objects.get(dni=dni)
            asistencia_data = {
                'fecha': date.today(),
                'tipo': tipo
            }
            
            # Pasar el usuario en el contexto
            serializer = AsistenciaSerializer(
                data=asistencia_data, 
                context={'request': request, 'usuario': usuario}
            )
            
            if serializer.is_valid():
                asistencia = serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Usuario.DoesNotExist:
            return Response({'detail': f'No se encontró un usuario con el DNI: {dni}'}, status=404)

class AsistenciaListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        usuario_id = request.query_params.get('usuario')  # Cambiado cliente a usuario
        fecha = request.query_params.get('fecha')

        asistencias = Asistencia.objects.all()

        if usuario_id:
            asistencias = asistencias.filter(usuario_id=usuario_id)  # Cambiado cliente a usuario
        if fecha:
            asistencias = asistencias.filter(fecha=fecha)

        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data)

class AsistenciaPorSalonAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, salon_id):
        try:
            # Obtener fechas o usar el día actual
            fecha_inicio = request.query_params.get('fecha_inicio')
            fecha_fin = request.query_params.get('fecha_fin')
            
            # Si no hay fechas, usar el día actual
            hoy = timezone.now().date()
            if not fecha_inicio and not fecha_fin:
                fecha_inicio = hoy
                fecha_fin = hoy
            
            # Obtener las membresías activas del salón
            membresias = Membresia.objects.filter(
                salon_id=salon_id,
                fecha_inicio__lte=fecha_fin,  # La membresía debe haber iniciado antes o en la fecha final
                fecha_fin__gte=fecha_inicio   # La membresía debe terminar después o en la fecha inicial
            )
            
            # Obtener usuarios con membresías activas
            usuarios = list(membresias.values_list('usuario', flat=True).distinct())
            
            # Obtener asistencias de estos usuarios para el rango de fechas
            asistencias = Asistencia.objects.filter(
                usuario_id__in=usuarios,
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin
            ).select_related('usuario').order_by('-fecha', '-hora')
                
            serializer = AsistenciaSerializer(asistencias, many=True)
            return Response({
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'total_asistencias': asistencias.count(),
                'total_usuarios': len(usuarios),
                'asistencias': serializer.data
            })
            
        except Exception as e:
            return Response(
                {"detail": f"Error obteniendo asistencias: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
