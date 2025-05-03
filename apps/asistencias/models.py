from django.db import models
from apps.users.models import Usuario

class Asistencia(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='entrada')
    registrado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='asistencias_registradas'
    )

    class Meta:
        unique_together = ['usuario', 'fecha']  # evita duplicados en el mismo día
        ordering = ['-fecha', '-hora']  # orden por fecha descendente

    def __str__(self):
        return f"Asistencia de {self.usuario.nombres} {self.usuario.apellidos} el {self.fecha}"
