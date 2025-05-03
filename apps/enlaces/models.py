from django.db import models
from apps.membresias.models import Salon

class EnlaceClaseGrabada(models.Model):
    salon = models.ForeignKey(
        Salon, 
        on_delete=models.CASCADE, 
        related_name='grabaciones'
    )
    link = models.URLField(max_length=500, blank=True, null=True)  # Made optional
    detalles = models.TextField(blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        fecha = self.fecha_subida.strftime('%Y-%m-%d') if self.fecha_subida else 'Sin fecha'
        return f"Grabación de {self.salon} - {fecha}"


    class Meta:
        verbose_name = "Enlace de Clase Grabada"
        verbose_name_plural = "Enlaces de Clases Grabadas"
        ordering = ['-fecha_subida']

class EnlaceCurso(models.Model):
    salon = models.ForeignKey(
        Salon, 
        on_delete=models.CASCADE, 
        related_name='cursos_grabados'
    )
    nombre_curso = models.CharField(max_length=200)
    link = models.URLField(max_length=500, blank=True, null=True)  # Made optional
    fecha_subida = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_curso} - {self.salon}"

    class Meta:
        verbose_name = "Enlace de Curso"
        verbose_name_plural = "Enlaces de Cursos"
        ordering = ['-fecha_subida']
