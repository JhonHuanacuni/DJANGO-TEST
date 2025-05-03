from rest_framework import serializers
from .models import Categoria, Curso, Examen, Pregunta, Alternativa, Nota

class AlternativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternativa
        fields = ['id', 'texto', 'es_correcta', 'puntaje']
        read_only_fields = ['id']

    def validate_puntaje(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El puntaje no puede ser negativo")
        return value

class PreguntaSerializer(serializers.ModelSerializer):
    alternativas = AlternativaSerializer(many=True)

    class Meta:
        model = Pregunta
        fields = ['id', 'texto', 'area', 'alternativas']
        read_only_fields = ['id']

    def validate_alternativas(self, value):
        if len(value) != 5:
            raise serializers.ValidationError("Debe haber exactamente 5 alternativas")
        
        correctas = sum(1 for alt in value if alt.get('es_correcta', False))
        if correctas != 1:
            raise serializers.ValidationError("Debe haber exactamente una alternativa correcta")
        
        return value

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['id', 'nombre', 'descripcion']

class CategoriaSerializer(serializers.ModelSerializer):
    cursos = CursoSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'cursos']

class ExamenSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True)

    class Meta:
        model = Examen
        fields = ['id', 'titulo', 'descripcion', 'tipo', 'fecha_inicio', 
                 'fecha_fin', 'tiempo_limite', 'visible', 'preguntas']
        read_only_fields = ['id']

    def validate_tipo(self, value):
        if value not in [40, 100]:
            raise serializers.ValidationError("El tipo debe ser 40 o 100")
        return value

    def validate_fechas(self, attrs):
        if attrs['fecha_inicio'] >= attrs['fecha_fin']:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        return attrs

    def validate_preguntas(self, value):
        tipo = self.initial_data.get('tipo')
        if tipo == 40 and len(value) != 40:
            raise serializers.ValidationError("El examen de 40 preguntas debe tener exactamente 40 preguntas")
        elif tipo == 100 and len(value) != 100:
            raise serializers.ValidationError("El examen de 100 preguntas debe tener exactamente 100 preguntas")
        return value

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
            'fecha_fin', 'tiempo_limite'
        ]

class NotaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source='estudiante.username', read_only=True)
    examen_titulo = serializers.CharField(source='examen.titulo', read_only=True)

    class Meta:
        model = Nota
        fields = ['id', 'estudiante', 'estudiante_nombre', 'examen', 'examen_titulo', 
                 'puntaje', 'porcentaje', 'correctas', 'incorrectas', 'no_respuesta',
                 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        examen = data.get('examen')
        estudiante = data.get('estudiante')
        
        if Nota.objects.filter(examen=examen, estudiante=estudiante).exists():
            raise serializers.ValidationError("Ya existe una nota para este estudiante en este examen")
        
        return data 