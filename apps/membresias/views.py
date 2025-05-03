from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone  # Agregar esta importación
from apps.membresias.models import Membresia, Salon, PagoMembresia
from apps.membresias.serializers import MembresiaSerializer, SalonSerializer, PagoMembresiaSerializer
from apps.users.permissions.roles import IsAdmin, IsSecretario, IsUsuario

class MembresiaListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membresias = Membresia.objects.all().select_related('usuario')  # Cambiado cliente a usuario
        serializer = MembresiaSerializer(membresias, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.rol not in ['admin', 'secretario']:
            return Response({'detail': 'No tienes permiso para registrar membresías.'}, status=403)

        try:
            data = request.data.copy()
            print("Datos recibidos en la vista:", data)  # Debug

            # Validación explícita del usuario
            usuario_id = data.get('usuario')
            if not usuario_id:
                return Response({'usuario': 'Este campo es requerido.'}, status=400)

            # Convertir usuario_id a entero si es necesario
            try:
                data['usuario'] = int(usuario_id)
            except (TypeError, ValueError):
                return Response({'usuario': 'ID de usuario inválido.'}, status=400)

            # Agregar registrada_por
            data['registrada_por'] = request.user.id
            
            print("Datos procesados:", data)  # Debug
            
            serializer = MembresiaSerializer(data=data)
            if serializer.is_valid():
                membresia = serializer.save()
                return Response(serializer.data, status=201)
            
            print("Errores de validación:", serializer.errors)  # Debug
            return Response(serializer.errors, status=400)
        
        except Exception as e:
            print(f"Error inesperado: {str(e)}")  # Debug
            return Response({'detail': str(e)}, status=500)


class MembresiaRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Membresia.objects.select_related('usuario').get(pk=pk)
        except Membresia.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        membresia = self.get_object(pk)
        serializer = MembresiaSerializer(membresia)
        return Response(serializer.data)

    def put(self, request, pk):
        membresia = self.get_object(pk)
        if request.user.rol not in ['admin', 'secretario']:
            return Response({
                'detail': 'No tienes permiso para actualizar membresías.'
            }, status=403)

        serializer = MembresiaSerializer(membresia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        membresia = self.get_object(pk)
        if request.user.rol != 'admin':
            return Response({
                'detail': 'Solo los administradores pueden eliminar membresías.'
            }, status=403)
        membresia.delete()
        return Response(status=204)



""" PAGO MEMBRESIA """

class PagoMembresiaCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.rol not in ['admin', 'secretario']:
            return Response({'detail': 'No tienes permiso para registrar pagos.'}, status=403)

        serializer = PagoMembresiaSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class PagosPorMembresiaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, membresia_id):
        pagos = PagoMembresia.objects.filter(membresia_id=membresia_id)
        serializer = PagoMembresiaSerializer(pagos, many=True)
        return Response(serializer.data)
    
class PagosListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            pagos = PagoMembresia.objects.select_related('membresia__usuario', 'registrado_por').all()
            serializer = PagoMembresiaSerializer(pagos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": f"Error obteniendo pagos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

""" SALONES """

class SalonViewSet(APIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsSecretario]

    def get(self, request):
        salones = Salon.objects.all()
        serializer = SalonSerializer(salones, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SalonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class SalonDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsSecretario]

    def get_object(self, pk):
        return get_object_or_404(Salon, pk=pk)

    def get_salon_usuarios(self, salon):
        # Obtener membresías activas del salón
        membresias_activas = salon.membresias.filter(fecha_fin__gte=timezone.now().date())
        # Extraer usuarios únicos de esas membresías
        usuarios = [membresia.usuario for membresia in membresias_activas]
        return usuarios

    def get(self, request, pk):
        salon = self.get_object(pk)
        # Verificar si se solicitan los usuarios
        if request.query_params.get('usuarios'):
            usuarios = self.get_salon_usuarios(salon)
            usuarios_data = [{
                'id': usuario.id,
                'username': usuario.username,
                'nombres': usuario.nombres,
                'apellidos': usuario.apellidos,
                'dni': usuario.dni
            } for usuario in usuarios]
            return Response({
                'salon': SalonSerializer(salon).data,
                'usuarios': usuarios_data
            })
        # Si no se solicitan usuarios, retorna solo la info del salón
        serializer = SalonSerializer(salon)
        return Response(serializer.data)

    def put(self, request, pk):
        salon = self.get_object(pk)
        serializer = SalonSerializer(salon, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        salon = self.get_object(pk)
        salon.delete()
        return Response(status=204)

class SalonRemoveUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        salon = get_object_or_404(Salon, pk=pk)
        usuario_id = request.data.get('usuario_id')
        
        if not usuario_id:
            return Response({'detail': 'ID de usuario requerido'}, status=400)
            
        try:
            membresia = Membresia.objects.get(
                salon=salon,
                usuario_id=usuario_id,
                fecha_fin__gte=timezone.now().date()
            )
            membresia.salon = None
            membresia.save()
            return Response({'detail': 'Usuario removido exitosamente'}, status=200)
        except Membresia.DoesNotExist:
            return Response(
                {'detail': 'No se encontró una membresía activa para este usuario en este salón'},
                status=404
            )


class SalonPublicViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        salones = Salon.objects.all()
        serializer = SalonSerializer(salones, many=True)
        return Response(serializer.data)