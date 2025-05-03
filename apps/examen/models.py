from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.users.models import Usuario

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='cursos')
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Examen(models.Model):
    TIPO_CHOICES = [
        (40, '40 preguntas'),
        (100, '100 preguntas')
    ]

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    tipo = models.IntegerField(choices=TIPO_CHOICES)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    tiempo_limite = models.IntegerField(help_text="Tiempo en minutos")
    visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"

class Pregunta(models.Model):
    AREA_CHOICES = [
        ('act', 'ACT'),
        ('hm', 'Habilidad Matemática'),
        ('hv', 'Habilidad Verbal'),
        ('arit', 'Aritmética'),
        ('geo', 'Geometría'),
        ('alge', 'Álgebra'),
        ('trigo', 'Trigonometría'),
        ('lengua', 'Lenguaje'),
        ('lit', 'Literatura'),
        ('psi', 'Psicología'),
        ('civ', 'Cívica'),
        ('hp', 'Historia del Perú'),
        ('hu', 'Historia Universal'),
        ('geo_l', 'Geografía'),
        ('eco', 'Economía'),
        ('filo', 'Filosofía'),
        ('fis', 'Física'),
        ('qui', 'Química'),
        ('bio', 'Biología')
    ]

    texto = models.TextField()
    area = models.CharField(max_length=10, choices=AREA_CHOICES)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='preguntas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pregunta {self.id} - {self.get_area_display()}"

    class Meta:
        ordering = ['id']

class Alternativa(models.Model):
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='alternativas')
    puntaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    orden = models.PositiveIntegerField(default=1)  # Campo requerido para el cálculo de puntaje
    created_at = models.DateTimeField(default=timezone.now)  # Temporal para migración
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.texto} - {'Correcta' if self.es_correcta else 'Incorrecta'}"

    class Meta:
        ordering = ['id']

class Nota(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notas_examen')
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='notas')
    puntaje = models.DecimalField(max_digits=5, decimal_places=2)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    correctas = models.IntegerField()
    incorrectas = models.IntegerField()
    no_respuesta = models.IntegerField()
    detalle_areas = models.JSONField(default=dict)  # Campo nuevo para almacenar resultados por área
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.estudiante.username} - {self.examen.titulo} - {self.porcentaje}%"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['estudiante', 'examen']