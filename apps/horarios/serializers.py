from rest_framework import serializers
from apps.horarios.models import Horario

class HorarioSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(required=False)
    is_file_modified = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Horario
        fields = '__all__'

    def create(self, validated_data):
        # Remover is_file_modified antes de crear
        validated_data.pop('is_file_modified', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Remover is_file_modified del validated_data si existe
        is_file_modified = validated_data.pop('is_file_modified', False)
        
        # Si no hay nueva imagen y no es file_modified, evitar actualizar el campo imagen
        if not is_file_modified and 'imagen' in validated_data:
            validated_data.pop('imagen')
        
        return super().update(instance, validated_data)