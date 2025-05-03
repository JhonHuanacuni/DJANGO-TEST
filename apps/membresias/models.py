from django.db import models
from apps.users.models import Usuario
from django.utils import timezone

# Opciones para los campos de elección
PLAN_CHOICES = [
    ('Plan Anual 1 (Mañana)', 'Plan Anual 1 (Mañana)'),
    ('Plan Anual 2 (Tarde)', 'Plan Anual 2 (Tarde)'),
    ('Plan Anual 3 (Mañana)', 'Plan Anual 3 (Mañana)'),
    ('Plan Anual Virtual (Mañana)', 'Plan Anual Virtual (Mañana)'),
    ('Plan Escolar 1 (Interdiario Mañana)', 'Plan Escolar 1 (Interdiario Mañana)'),
    ('Plan Escolar 2 (Interdiario Tarde)', 'Plan Escolar 2 (Interdiario Tarde)'),
    ('Plan Sabatino 1 (Mañana)', 'Plan Sabatino 1 (Mañana)'),
    ('Plan Semestral 1 (Mañana)', 'Plan Semestral 1 (Mañana)'),
    ('Plan Beca 18 (Mañana)', 'Plan Beca 18 (Mañana)'),
]

TIPO_CHOICES = [
    ('Individual', 'Individual'),
    ('Duo', 'Duo'),
    ('Trío', 'Trío'),
]

TIPO_PAGO_CHOICES = [
    ('Efectivo', 'Efectivo'),
    ('Tarjeta', 'Tarjeta'),
    ('Transferencia', 'Transferencia'),
    ('Yape', 'Yape'),
    ('Plin', 'Plin'),
    ('Otros', 'Otros'),
]

class Salon(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    capacidad = models.IntegerField(default=20)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Salón'
        verbose_name_plural = 'Salones'

class Membresia(models.Model):
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='membresias',
        null=False  # Asegurarnos que no sea null
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    monto_total = models.DecimalField(max_digits=8, decimal_places=2, default=120.00)
    
    plan = models.CharField(max_length=40, choices=PLAN_CHOICES, default='Plan Anual 1 (Mañana)')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Individual')
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, default='Efectivo')

    fecha_registro = models.DateTimeField(default=timezone.now)
    observaciones = models.TextField(blank=True, null=True)

    registrada_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='membresias_registradas')

    salon = models.ForeignKey(
        Salon, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='membresias'
    )

    def __str__(self):
        return f"Membresía de {self.usuario.username} {self.usuario.apellidos}"
    
    @property
    def total_pagado(self):
        return sum(pago.monto_pagado for pago in self.pagos.all())

    @property
    def estado(self):
        hoy = timezone.now().date()
        if hoy > self.fecha_fin:
            return "vencida"
        elif self.total_pagado < self.monto_total:
            return "con deuda"
        else:
            return "activa"
    
    def tiene_membresia_activa(self):
        hoy = timezone.now().date()
        return self.fecha_fin >= hoy and self.estado != "vencida"
    
    def tiene_deuda(self):
        return self.total_pagado < self.monto_total

    def saldo_pendiente(self):
        return self.monto_total - self.total_pagado

    def clean(self):
        from django.core.exceptions import ValidationError
        # Verificar si el usuario ya tiene una membresía activa
        membresia_activa = Membresia.objects.filter(
            usuario=self.usuario,
            fecha_fin__gte=timezone.now().date()
        ).exclude(id=self.id).exists()
        
        if membresia_activa:
            raise ValidationError('Este usuario ya tiene una membresía activa.')

class PagoMembresia(models.Model):
    membresia = models.ForeignKey(Membresia, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateField(auto_now_add=True)
    monto_pagado = models.DecimalField(max_digits=8, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='pagos_registrados')

    def __str__(self):
        return f"Pago de {self.monto_pagado} para {self.membresia}"
