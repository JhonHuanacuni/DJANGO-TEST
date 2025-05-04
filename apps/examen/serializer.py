from rest_framework import serializers
from .models import Categoria, Curso, Examen, Pregunta, Alternativa, Nota

class AlternativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternativa
        fields = ['id', 'texto', 'es_correcta', 'puntaje', 'orden']
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
    preguntas = PreguntaSerializer(many=True, required=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='curso.categoria.nombre', read_only=True)

    class Meta:
        model = Examen
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'curso', 'curso_nombre', 
            'categoria_nombre', 'visible', 'fecha_inicio', 'fecha_fin', 
            'tiempo_limite', 'preguntas', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        
        # Validar fechas
        if data.get('fecha_inicio') and data.get('fecha_fin'):
            if data['fecha_inicio'] >= data['fecha_fin']:
                errors['fechas'] = "La fecha de inicio debe ser anterior a la fecha de fin"
        
        # Validar tiempo límite
        if data.get('tiempo_limite') is not None:
            if data['tiempo_limite'] <= 0:
                errors['tiempo_limite'] = "El tiempo límite debe ser mayor a 0"
        
        # Validar número de preguntas
        preguntas_count = len(data.get('preguntas', []))
        if data.get('tipo') is not None:
            if preguntas_count != data['tipo']:
                errors['preguntas'] = f"El número de preguntas debe ser {data['tipo']}"
        
        # Validar curso
        if not data.get('curso'):
            errors['curso'] = "Debe seleccionar un curso"
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

    def create(self, validated_data):
        try:
            preguntas_data = validated_data.pop('preguntas')
            examen = Examen.objects.create(**validated_data)
            
            for pregunta_data in preguntas_data:
                alternativas_data = pregunta_data.pop('alternativas')
                pregunta = Pregunta.objects.create(examen=examen, **pregunta_data)
                
                for alternativa_data in alternativas_data:
                    Alternativa.objects.create(pregunta=pregunta, **alternativa_data)
            
            return examen
        except Exception as e:
            raise serializers.ValidationError(f"Error al crear el examen: {str(e)}")

class ExamenListSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='curso.categoria.nombre', read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Examen
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'curso_nombre', 
            'categoria_nombre', 'visible', 'esta_activo', 'fecha_inicio', 
            'fecha_fin', 'tiempo_limite', 'created_at'
        ]

class NotaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source='estudiante.get_full_name', read_only=True)
    examen_titulo = serializers.CharField(source='examen.titulo', read_only=True)
    curso_nombre = serializers.CharField(source='examen.curso.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='examen.curso.categoria.nombre', read_only=True)

    class Meta:
        model = Nota
        fields = [
            'id', 'estudiante', 'estudiante_nombre', 'examen', 'examen_titulo',
            'curso_nombre', 'categoria_nombre', 'puntaje', 'porcentaje',
            'correctas', 'incorrectas', 'no_respuesta', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        examen = data.get('examen')
        estudiante = data.get('estudiante')
        
        if Nota.objects.filter(examen=examen, estudiante=estudiante).exists():
            raise serializers.ValidationError("Ya existe una nota para este estudiante en este examen")
        
        return data 