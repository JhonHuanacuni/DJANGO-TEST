from rest_framework import serializers
from apps.users.serializers import UsuarioSerializer
from apps.membresias.models import Membresia, Salon
from apps.membresias.models import Membresia, PagoMembresia
from django.utils import timezone

class PagoMembresiaSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()
    registrado_por = serializers.SerializerMethodField()
    
    class Meta:
        model = PagoMembresia
        # Se listan explícitamente los campos para incluir los nuevos
        fields = ['id', 'membresia', 'fecha_pago', 'monto_pagado', 'observaciones', 'usuario', 'registrado_por']
        read_only_fields = ('registrado_por',)
    
    def get_usuario(self, obj):
        # Retorna la información completa del usuario de la membresía
        if obj.membresia and obj.membresia.usuario:
            return {
                'id': obj.membresia.usuario.id,
                'username': obj.membresia.usuario.username,
                'nombres': obj.membresia.usuario.nombres or '',  # Agregado nombres
                'apellidos': obj.membresia.usuario.apellidos or ''
            }
        return None
    
    def get_registrado_por(self, obj):
        if obj.registrado_por:
            return {
                'id': obj.registrado_por.id,
                'username': obj.registrado_por.username,
                'nombres': obj.registrado_por.nombres or '',
                'apellidos': obj.registrado_por.apellidos or ''
            }
        return None
    
    def create(self, validated_data):
        validated_data['registrado_por'] = self.context['user']
        return super().create(validated_data)
    
    def validate(self, data):
        membresia = data['membresia']
        total_pagado = membresia.total_pagado
        nuevo_pago = data['monto_pagado']
        if total_pagado + nuevo_pago > membresia.monto_total:
            raise serializers.ValidationError("Este pago excede el monto total de la membresía.")
        return data


class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = ['id', 'nombre', 'descripcion', 'capacidad', 'activo']


class MembresiaSerializer(serializers.ModelSerializer):
    salon_detalle = SalonSerializer(source='salon', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Membresia
        fields = [
            'id', 'usuario', 'fecha_inicio', 'fecha_fin',
            'monto_total', 'tipo', 'plan', 'tipo_pago',
            'observaciones', 'registrada_por', 'estado',
            'total_pagado', 'pagos', 'salon', 'salon_detalle',
            'created_at'
        ]
        read_only_fields = ['id', 'estado', 'total_pagado', 'pagos', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.usuario:
            data['usuario'] = {
                'id': instance.usuario.id,
                'username': instance.usuario.username,
                'nombres': instance.usuario.nombres,
                'apellidos': instance.usuario.apellidos,
                'dni': instance.usuario.dni if hasattr(instance.usuario, 'dni') else None
            }
        if instance.registrada_por:
            data['registrada_por_detalle'] = {
                'id': instance.registrada_por.id,
                'username': instance.registrada_por.username,
                'nombres': instance.registrada_por.nombres,
                'apellidos': instance.registrada_por.apellidos
            }
        return data

    def validate(self, data):
        # Para actualizaciones parciales, obtener los valores actuales si no están en data
        if self.instance:  # Si es una actualización
            fecha_inicio = self.instance.fecha_inicio
            fecha_fin = data.get('fecha_fin', self.instance.fecha_fin)
        else:  # Si es una creación
            fecha_inicio = data.get('fecha_inicio')
            fecha_fin = data.get('fecha_fin')
            
            if not fecha_inicio or not fecha_fin:
                raise serializers.ValidationError("Las fechas son requeridas para crear una membresía")

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise serializers.ValidationError("La fecha de inicio no puede ser mayor a la fecha de fin.")

        return data


