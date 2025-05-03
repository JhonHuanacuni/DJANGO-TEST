from rest_framework import serializers
from apps.asistencias.models import Asistencia
from apps.users.serializers import UsuarioSerializer
from datetime import date

class AsistenciaSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    salon = serializers.SerializerMethodField()

    class Meta:
        model = Asistencia
        fields = ['id', 'usuario', 'fecha', 'hora', 'tipo', 'registrado_por', 'salon']
        read_only_fields = ['registrado_por', 'salon']

    def get_salon(self, obj):
        # Obtener la membresía activa del usuario
        membresia_activa = obj.usuario.membresias.filter(
            fecha_inicio__lte=obj.fecha,
            fecha_fin__gte=obj.fecha,
            salon__isnull=False
        ).first()
        
        if membresia_activa and membresia_activa.salon:
            return {
                'id': membresia_activa.salon.id,
                'nombre': membresia_activa.salon.nombre
            }
        return None
    
    def validate(self, data):
        # Obtener el usuario del contexto
        usuario = self.context.get('usuario')
        if not usuario:
            raise serializers.ValidationError("Se requiere un usuario válido")

        fecha = data.get('fecha', date.today())
        
        # Verificar si ya existe asistencia
        if Asistencia.objects.filter(usuario=usuario, fecha=fecha).exists():
            raise serializers.ValidationError("Ya se registró la asistencia de este usuario para hoy")
        
        data['fecha'] = fecha
        data['usuario'] = usuario
        if 'tipo' not in data:
            data['tipo'] = 'entrada'
        
        return data

    def create(self, validated_data):
        validated_data['registrado_por'] = self.context['request'].user
        return super().create(validated_data)
