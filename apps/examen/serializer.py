from rest_framework import serializers
from apps.examen.models import Categoria, Curso, Examen, Pregunta, Alternativa

class AlternativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternativa
        fields = ['id', 'texto', 'es_correcta']

class PreguntaSerializer(serializers.ModelSerializer):
    alternativas = AlternativaSerializer(many=True, required=True)

    class Meta:
        model = Pregunta
        fields = ['id', 'texto', 'area', 'alternativas']

    def validate_alternativas(self, value):
        if len(value) != 5:
            raise serializers.ValidationError("Debe haber exactamente 5 alternativas por pregunta")
        
        correctas = sum(1 for alt in value if alt['es_correcta'])
        if correctas != 1:
            raise serializers.ValidationError("Debe haber exactamente una alternativa correcta")
        
        return value

class ExamenSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True, required=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='curso.categoria.nombre', read_only=True)

    class Meta:
        model = Examen
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'curso', 'curso_nombre', 
            'categoria_nombre', 'activo', 'fecha_inicio', 'fecha_fin', 
            'tiempo_limite', 'preguntas', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        if data['fecha_inicio'] >= data['fecha_fin']:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        if data['tiempo_limite'] <= 0:
            raise serializers.ValidationError("El tiempo límite debe ser mayor a 0")
        
        preguntas_count = len(data.get('preguntas', []))
        if preguntas_count != data['tipo']:
            raise serializers.ValidationError(f"El número de preguntas debe ser {data['tipo']}")
        
        return data

    def create(self, validated_data):
        preguntas_data = validated_data.pop('preguntas')
        examen = Examen.objects.create(**validated_data)
        
        for pregunta_data in preguntas_data:
            alternativas_data = pregunta_data.pop('alternativas')
            pregunta = Pregunta.objects.create(examen=examen, **pregunta_data)
            
            for alternativa_data in alternativas_data:
                Alternativa.objects.create(pregunta=pregunta, **alternativa_data)
        
        return examen

class ExamenListSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='curso.categoria.nombre', read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Examen
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'curso_nombre', 
            'categoria_nombre', 'activo', 'esta_activo', 'fecha_inicio', 
            'fecha_fin', 'tiempo_limite', 'created_at'
        ]