from django.contrib.auth.models import AbstractUser
from django.db import models
import qrcode
from django.conf import settings
import os

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('secretario', 'Secretario'),
        ('usuario', 'Usuario'),
    )
    MODOS = (
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    nombres = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo de nombres
    apellidos = models.CharField(max_length=100, blank=True, null=True)
    dni = models.CharField(max_length=8, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=150, blank=True, null=True)
    telefono_apoderado = models.CharField(max_length=20, blank=True, null=True)
    modo = models.CharField(max_length=20, choices=MODOS, default='presencial')

    def __str__(self):
        return f"{self.username} ({self.rol})"

    def generar_qr(self):
        if not self.dni:
            return None
            
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.dni)
            qr.make(fit=True)

            # Crear la imagen QR
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Usar MEDIA_ROOT y QRCODES_DIR de settings
            qr_folder = os.path.join(settings.MEDIA_ROOT, settings.QRCODES_DIR)
            
            # Crear el directorio si no existe
            os.makedirs(qr_folder, exist_ok=True)
            
            # Generar nombre de archivo
            qr_filename = f'qr_{self.dni}.png'
            qr_path = os.path.join(qr_folder, qr_filename)
            
            # Guardar la imagen
            img.save(qr_path)
            
            # Retornar la ruta relativa para la URL
            return f'{settings.QRCODES_DIR}/{qr_filename}'
        except Exception as e:
            print(f"Error generando QR: {str(e)}")
            return None