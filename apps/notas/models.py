from django.db import models
from apps.users.models import Usuario

class ImportacionNotas(models.Model):
    fecha_importacion = models.DateTimeField(auto_now_add=True)
    importado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    nombre_archivo = models.CharField(max_length=255, help_text="Nombre del archivo de referencia")

    def __str__(self):
        return f"Importación {self.nombre_archivo} - {self.fecha_importacion}"

class Nota(models.Model):
    MODO_CHOICES = [
        ("presencial", "Presencial"),
        ("virtual", "Virtual"),
    ]
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notas')
    modo = models.CharField(max_length=20, choices=MODO_CHOICES, default="presencial", help_text="Modalidad del examen: presencial o virtual")
    puntaje = models.DecimalField(max_digits=7, decimal_places=2)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    correctas = models.IntegerField()
    incorrectas = models.IntegerField()
    no_respuesta = models.IntegerField()
    act = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    hm = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    hv = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    arit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    geo = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    alge = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    trigo = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lengua = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    lit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    psi = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    civ = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    hp = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    hu = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    geo_l = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    eco = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    filo = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fis = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    qui = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    bio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descripcion = models.TextField(blank=True, null=True)
    importacion = models.ForeignKey(ImportacionNotas, on_delete=models.CASCADE, related_name='notas')

    class Meta:
        ordering = ['-id']

