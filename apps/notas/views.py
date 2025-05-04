from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView
from apps.notas.serializer import NotaBulkImportWithImportacionSerializer, NotaSerializer
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions.roles import IsAdmin, IsSecretario, IsUsuario


from apps.notas.models import ImportacionNotas, Nota

class NotaBulkImportView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = NotaBulkImportWithImportacionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            notas = serializer.save()
            return Response({'created': len(notas)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImportacionNotasListView(ListAPIView):
    queryset = ImportacionNotas.objects.all().order_by('-fecha_importacion')
    permission_classes = [permissions.IsAuthenticated, IsAdmin | IsSecretario]
    
    def get(self, request, *args, **kwargs):
        try:
            data = [
                {
                    'id': imp.id,
                    'fecha_importacion': imp.fecha_importacion.isoformat(),
                    'importado_por': str(imp.importado_por) if imp.importado_por else None,
                    'nombre_archivo': imp.nombre_archivo,
                    'salon': {
                        'id': imp.salon.id,
                        'nombre': imp.salon.nombre,
                        'capacidad': imp.salon.capacidad,
                        'activo': imp.salon.activo
                    } if imp.salon else None
                } for imp in self.get_queryset()
            ]
            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NotasPorImportacionListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, importacion_id, *args, **kwargs):
        notas = Nota.objects.filter(importacion_id=importacion_id)
        AREAS = [
            ('ACT', 'act'), ('HV', 'hv'), ('HM', 'hm'),
            ('ARIT', 'arit'), ('GEOM', 'geo'), ('ALGE', 'alge'), ('TRIGO', 'trigo'),
            ('LEN', 'lengua'), ('LIT', 'lit'), ('PSI', 'psi'), ('CIV', 'civ'), ('HP', 'hp'), ('HU', 'hu'),
            ('GEOG', 'geo_l'), ('ECO', 'eco'), ('FILO', 'filo'),
            ('FIS', 'fis'), ('QUI', 'qui'), ('BIO', 'bio')
        ]
        data = []
        for n in notas:
            # Primero, agregar la nota total del examen
            data.append({
                'id': n.id,
                'estudiante': str(n.estudiante),
                'puntaje': float(n.puntaje),  # Puntaje total
                'porcentaje': n.porcentaje,
                'fecha_importacion': n.importacion.fecha_importacion.isoformat(),
                'importacion_id': n.importacion.id,
                'curso': None,  # Nota total, no es de área
                'puntaje_area': None
            })
            # Luego, agregar las notas por área como antes
            for codigo, campo in AREAS:
                puntaje_area = getattr(n, campo, None)
                if puntaje_area is not None:
                    data.append({
                        'id': n.id,
                        'estudiante': str(n.estudiante),
                        'nombre_estudiante': f"{n.estudiante.nombres} {n.estudiante.apellidos}".strip(),
                        'puntaje': float(puntaje_area),
                        'porcentaje': n.porcentaje,
                        'fecha_importacion': n.importacion.fecha_importacion.isoformat(),
                        'importacion_id': n.importacion.id,
                        'curso': codigo,
                        'puntaje_area': float(puntaje_area),
                    })
        return Response(data)

# Nuevo endpoint para notas del usuario autenticado
class MisNotasAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsSecretario | IsUsuario ]
    def get(self, request):
        usuario = request.user
        notas = Nota.objects.filter(estudiante=usuario).order_by('-importacion__fecha_importacion', '-id')
        historial = NotaSerializer(notas, many=True).data
        nota_reciente = historial[0] if historial else None
        return Response({
            'nota_reciente': nota_reciente,
            'historial': historial
        })