from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from apps.examen.models import Categoria, Curso, Examen, Pregunta, Alternativa, Nota
from apps.examen.serializer import (
    CategoriaSerializer, CursoSerializer, ExamenSerializer,
    PreguntaSerializer, AlternativaSerializer, NotaSerializer
)
from apps.users.models import Usuario
from decimal import Decimal
from rest_framework.exceptions import PermissionDenied

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        categoria_id = self.request.query_params.get('categoria', None)
        if categoria_id:
            return Curso.objects.filter(categoria_id=categoria_id)
        return Curso.objects.all()

class ExamenViewSet(viewsets.ModelViewSet):
    queryset = Examen.objects.all()
    serializer_class = ExamenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Examen.objects.all()
        if not self.request.user.is_staff:
            ahora = timezone.now()
            queryset = queryset.filter(
                visible=True,
                fecha_inicio__lte=ahora,
                fecha_fin__gte=ahora
            )
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Solo los administradores pueden crear exámenes")
        serializer.save(creado_por=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Solo los administradores pueden modificar exámenes")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Solo los administradores pueden eliminar exámenes")
        instance.delete()

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        if not request.user.is_staff:
            raise PermissionDenied("Solo los administradores pueden activar exámenes")
        examen = self.get_object()
        examen.visible = True
        examen.save()
        return Response({'status': 'examen activado'})

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        if not request.user.is_staff:
            raise PermissionDenied("Solo los administradores pueden desactivar exámenes")
        examen = self.get_object()
        examen.visible = False
        examen.save()
        return Response({'status': 'examen desactivado'})

    @action(detail=True, methods=['post'], url_path='enviar-respuestas')
    def enviar_respuestas(self, request, pk=None):
        """
        Recibe las respuestas del estudiante, corrige el examen y guarda la Nota.
        request.data = {
            'respuestas': [ { 'pregunta_id': int, 'alternativa_id': int }, ... ]
        }
        """
        examen = self.get_object()
        usuario = request.user
        respuestas = request.data.get('respuestas', [])
        if not respuestas or not isinstance(respuestas, list):
            return Response({'error': 'Respuestas inválidas'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar fechas y visibilidad
        ahora = timezone.now()
        if not examen.visible or ahora < examen.fecha_inicio or ahora > examen.fecha_fin:
            return Response({'error': 'El examen no está activo'}, status=status.HTTP_403_FORBIDDEN)
        
        # Corregir respuestas
        puntaje_total = 0
        correctas = 0
        incorrectas = 0
        no_respuesta = 0
        
        for respuesta in respuestas:
            pregunta_id = respuesta.get('pregunta_id')
            alternativa_id = respuesta.get('alternativa_id')
            
            try:
                pregunta = Pregunta.objects.get(id=pregunta_id, examen=examen)
                if alternativa_id:
                    alternativa = Alternativa.objects.get(id=alternativa_id, pregunta=pregunta)
                    if alternativa.es_correcta:
                        correctas += 1
                        if examen.tipo == 100 and pregunta.area == 'act':
                            puntaje_total += alternativa.puntaje or 20
                        else:
                            puntaje_total += 20
                    else:
                        incorrectas += 1
                        puntaje_total -= 1.125
                else:
                    no_respuesta += 1
            except (Pregunta.DoesNotExist, Alternativa.DoesNotExist):
                return Response({'error': 'Pregunta o alternativa inválida'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calcular porcentaje
        total_preguntas = examen.tipo
        porcentaje = (puntaje_total / (total_preguntas * 20)) * 100
        
        # Crear nota
        nota = Nota.objects.create(
            estudiante=usuario,
            examen=examen,
            puntaje=puntaje_total,
            porcentaje=porcentaje,
            correctas=correctas,
            incorrectas=incorrectas,
            no_respuesta=no_respuesta
        )
        
        return Response({
            'puntaje': puntaje_total,
            'porcentaje': porcentaje,
            'correctas': correctas,
            'incorrectas': incorrectas,
            'no_respuesta': no_respuesta
        })

class PreguntaViewSet(viewsets.ModelViewSet):
    queryset = Pregunta.objects.all()
    serializer_class = PreguntaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        examen_id = self.request.query_params.get('examen', None)
        if examen_id:
            return Pregunta.objects.filter(examen_id=examen_id)
        return Pregunta.objects.none()

class AlternativaViewSet(viewsets.ModelViewSet):
    queryset = Alternativa.objects.all()
    serializer_class = AlternativaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pregunta_id = self.request.query_params.get('pregunta', None)
        if pregunta_id:
            return Alternativa.objects.filter(pregunta_id=pregunta_id)
        return Alternativa.objects.all()

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all()
    serializer_class = NotaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        examen_id = self.request.query_params.get('examen', None)
        
        if examen_id:
            # Si se especifica un examen, devolver todas las notas de ese examen
            return Nota.objects.filter(examen_id=examen_id).order_by('-created_at')
        
        if user.is_staff:
            return Nota.objects.all()
        return Nota.objects.filter(estudiante=user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
