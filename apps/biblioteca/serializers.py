from rest_framework import serializers
from apps.biblioteca.models import Libro

class LibroSerializer(serializers.ModelSerializer):
    archivo = serializers.FileField(required=False)
    portada = serializers.ImageField(required=False, allow_null=True)
    is_file_modified = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Libro
        fields = '__all__'

    def create(self, validated_data):
        # Para creación, removemos is_file_modified y creamos directamente
        validated_data.pop('is_file_modified', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Obtener y remover is_file_modified
        is_file_modified = validated_data.pop('is_file_modified', False)
        # Actualizar atributos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # Guardar con el flag
        instance.save(is_file_modified=is_file_modified)
        return instance