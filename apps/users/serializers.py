# users/serializers.py

from rest_framework import serializers
from apps.users.models import Usuario
from django.contrib.auth.hashers import make_password
import uuid
from django.conf import settings

class UsuarioSerializer(serializers.ModelSerializer):
    salon = serializers.SerializerMethodField()
    qr_url = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'nombres', 
                 'apellidos', 'dni', 'fecha_nacimiento', 'telefono', 
                 'telefono_apoderado', 'direccion', 'rol', 'qr_url', 'salon', 'modo']
        extra_kwargs = {'password': {'write_only': True}}

    def get_qr_url(self, obj):
        if obj.dni:
            return f'{settings.MEDIA_URL}qrcodes/qr_{obj.dni}.png'
        return None

    def get_salon(self, obj):
        # Obtener la membresía activa más reciente
        membresia = obj.membresias.order_by('-fecha_inicio').first()
        if membresia and membresia.salon:
            return {
                'id': membresia.salon.id,
                'nombre': membresia.salon.nombre
            }
        return None

    def create(self, validated_data):
        if not validated_data.get('username'):
            nombre = validated_data.get('nombres', '')
            base = ''.join(nombre.split()).lower() if nombre else 'user'
            validated_data['username'] = base + str(uuid.uuid4())[:8]
        validated_data['password'] = make_password(validated_data['password'])
        usuario = super().create(validated_data)
        
        # Generar QR después de crear el usuario
        if usuario.dni:
            usuario.generar_qr()
        
        return usuario

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Asegurarnos de que el QR esté incluido en la respuesta
        if instance.dni:
            data['qr_url'] = self.get_qr_url(instance)
        # Asegurarnos de que el teléfono de apoderado esté presente
        data['telefono_apoderado'] = getattr(instance, 'telefono_apoderado', None)
        return data
