from django.db import models
import os
import unicodedata
import re
from django.conf import settings
import glob

class Horario(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    @staticmethod
    def slugify_filename(filename):
        name, ext = os.path.splitext(filename)
        name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
        name = name.replace(' ', '-')
        name = name.lower()
        name = re.sub(r'[^\w.-]', '', name)
        name = re.sub(r'-+', '-', name)
        name = name.strip('-')
        return f"{name}{ext}"

    @classmethod
    def limpiar_archivos_huerfanos(cls):
        """Elimina los archivos de horarios que no están vinculados a ningún registro"""
        print("\n=== Analizando rutas ===")
        print(f"Directorio actual: {os.getcwd()}")
        print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
        
        # Usar ruta absoluta para buscar archivos
        patron_archivos = os.path.join(settings.MEDIA_ROOT, 'horarios', '*')
        print(f"Patrón de búsqueda absoluto: {patron_archivos}")
        
        archivos_existentes = glob.glob(patron_archivos)
        
        # Normalizar las rutas existentes
        archivos_existentes = [os.path.normpath(archivo) for archivo in archivos_existentes]
        
        print("\n=== Archivos existentes en el sistema ===")
        for archivo in archivos_existentes:
            print(f"Archivo en sistema: {archivo}")
        
        # Obtener todas las rutas de archivos en la base de datos
        archivos_db = set()
        for h in cls.objects.all():
            if h.imagen and h.imagen.name:
                ruta_completa = os.path.join(settings.MEDIA_ROOT, h.imagen.name)
                # Normalizar la ruta de la base de datos
                ruta_completa = os.path.normpath(ruta_completa)
                archivos_db.add(ruta_completa)
        
        print("\n=== Archivos registrados en la base de datos ===")
        for archivo in archivos_db:
            print(f"Archivo en DB: {archivo}")
        
        # Encontrar y eliminar archivos huérfanos
        print("\n=== Procesando archivos huérfanos ===")
        for archivo in archivos_existentes:
            if os.path.isfile(archivo) and archivo not in archivos_db:
                try:
                    print(f"Intentando eliminar archivo huérfano: {archivo}")
                    print(f"No encontrado en DB: {[db for db in archivos_db if os.path.basename(db) == os.path.basename(archivo)]}")
                    os.remove(archivo)
                except OSError as e:
                    print(f"Error al eliminar archivo huérfano {archivo}: {e}")

    def save(self, *args, **kwargs):
        """
        Procesa y guarda la imagen del horario:
        1. Normaliza el nombre del archivo
        2. Lo guarda en la carpeta 'horarios/'
        """
        if self.imagen and hasattr(self.imagen, 'name'):
            filename = os.path.basename(self.imagen.name)
            filename = self.slugify_filename(filename)
            self.imagen.name = os.path.join('horarios/', filename)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Elimina el horario y su archivo de imagen asociado
        """
        if self.imagen:
            self.imagen.delete(save=False)  # Elimina el archivo físico
        super().delete(*args, **kwargs)  # Elimina el registro de la base de datos

    def __str__(self):
        return self.titulo