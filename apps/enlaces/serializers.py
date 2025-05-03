from rest_framework import serializers
from apps.enlaces.models import EnlaceClaseGrabada, EnlaceCurso

class EnlaceClaseGrabadaSerializer(serializers.ModelSerializer):
    link = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = EnlaceClaseGrabada
        fields = '__all__'

class EnlaceCursoSerializer(serializers.ModelSerializer):
    link = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = EnlaceCurso
        fields = '__all__'
