from django.db import models
from pdf2image import convert_from_path
from django.core.files.base import ContentFile
from django.core.files import File
from io import BytesIO
import os
import unicodedata
import re
from django.core.files.storage import default_storage


class Libro(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='')
    portada = models.ImageField(upload_to='', blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    @staticmethod
    def slugify_filename(filename):
        # Quita extensión
        name, ext = os.path.splitext(filename)
        # Quita tildes
        name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
        # Reemplaza espacios por guion
        name = name.replace(' ', '-')
        # Solo minúsculas
        name = name.lower()
        # Quita caracteres no válidos (solo letras, números, guion, punto, guion bajo)
        name = re.sub(r'[^\w.-]', '', name)
        # Quita guiones múltiples
        name = re.sub(r'-+', '-', name)
        # Quita guiones al inicio/final
        name = name.strip('-')
        return f"{name}{ext}"

    @staticmethod
    def only_filename(filename):
        # Quita cualquier subdirectorio y deja solo el nombre
        return os.path.basename(filename)

    def save(self, *args, **kwargs):
        import logging
        logger = logging.getLogger("django")
        
        # Obtener el indicador del frontend
        is_file_modified = kwargs.pop('is_file_modified', False)
        logger.warning(f"[Libro.save] INICIO is_file_modified={is_file_modified}")
        
        # Modificar la detección de archivos nuevos
        archivo_nuevo = (
            self.pk is None or  # Es una creación nueva
            is_file_modified    # O el frontend indica que se modificó el archivo
        )
        
        # Simplificar la verificación de portada nueva
        try:
            portada_nueva = (
                self.pk is None or  # Es una creación nueva
                (self.portada and isinstance(self.portada, File))  # Es un archivo recién subido
            )
        except:
            portada_nueva = False

        logger.warning(f"[Libro.save] archivo_nuevo={archivo_nuevo}, archivo={self.archivo}")
        logger.warning(f"[Libro.save] portada_nueva={portada_nueva}, portada={self.portada}")

        # Si el PDF se reemplaza, borra la portada anterior (si existe)
        if archivo_nuevo and self.pk and self.portada:
            logger.warning(f"[Libro.save] Borrando portada antigua por nuevo PDF: {self.portada.name}")
            
            # Obtén el nombre base de la portada sin la extensión
            portada_base_name = os.path.splitext(self.only_filename(self.portada.name))[0]
            
            # Construye la ruta del archivo PDF con el mismo nombre que la portada
            pdf_to_delete = os.path.join('documents/', f"{portada_base_name}.pdf")
            
            # Intenta borrar el PDF actual aunque no se esté actualizando
            logger.warning(f"[Libro.save] archivo nuevo?: {is_file_modified} default_storage: {default_storage.exists(pdf_to_delete)}")
            if default_storage.exists(pdf_to_delete) and is_file_modified:
                logger.warning(f"[Libro.save] Borrando archivo PDF asociado a la portada: {pdf_to_delete}")
                default_storage.delete(pdf_to_delete)
            
            # Borra la portada antigua
            self.portada.delete(save=False)
            self.portada = None
            
        logger.warning(f"[Libro.save] Antes de renombrar - archivo={self.archivo}, portada={self.portada}")

        # Siempre maneja solo el nombre base
        if archivo_nuevo and self.archivo and hasattr(self.archivo, 'name'):
            filename = self.only_filename(self.archivo.name)
            filename = self.slugify_filename(filename)
            new_path = os.path.join('documents/', filename)

            # Verifica si ya existe un archivo con el mismo nombre y lo borra
            logger.warning(f"[Libro.save] Verificando existencia de archivo: {new_path}")
            if default_storage.exists(new_path):
                logger.warning(f"[Libro.save] Archivo existente encontrado, eliminando: {new_path}")
                default_storage.delete(new_path)

            self.archivo.name = new_path
            logger.warning(f"[Libro.save] Renombrando archivo: {self.archivo.name}")
        if portada_nueva and self.portada and hasattr(self.portada, 'name'):
            filename = self.only_filename(self.portada.name)
            filename = self.slugify_filename(filename)
            self.portada.name = os.path.join('documents/portadas/', filename)
            logger.warning(f"[Libro.save] Renombrando portada: {self.portada.name}")
        # Primero guardamos el modelo para asegurar que el archivo esté en el sistema
        super().save(*args, **kwargs)
        logger.warning(f"[Libro.save] Después de super().save - archivo={self.archivo}, portada={self.portada}")

        # Ahora intentamos generar la portada si es necesario
        if archivo_nuevo and self.archivo and not self.portada:
            try:
                logger.warning(f"[Libro.save] Generando portada automática para archivo {self.archivo}")
                # Asegurarnos de que el archivo existe
                if not os.path.exists(self.archivo.path):
                    logger.warning(f"[Libro.save] Esperando a que el archivo esté disponible...")
                    import time
                    time.sleep(1)  # Dar tiempo a que el archivo se escriba
                
                pdf_path = self.archivo.path
                images = convert_from_path(pdf_path, first_page=1, last_page=1)
                if images:
                    image = images[0]
                    buffer = BytesIO()
                    image.save(buffer, format='JPEG')
                    name = self.slugify_filename(os.path.splitext(self.only_filename(self.archivo.name))[0] + '.jpg')
                    portada_name = os.path.join('documents/portadas', name)
                    self.portada.save(portada_name, ContentFile(buffer.getvalue()), save=False)
                    logger.warning(f"[Libro.save] Portada generada y guardada: {portada_name}")
                    super().save(update_fields=['portada'])
            except Exception as e:
                logger.error(f"Error generating cover: {e}")
                # No relanzo la excepción para que al menos se guarde el PDF

        logger.warning(f"[Libro.save] FIN - archivo={self.archivo}, portada={self.portada}")

    def delete(self, *args, **kwargs):
        import logging
        logger = logging.getLogger("django")
        logger.warning(f"[Libro.delete] INICIO - archivo={self.archivo}, portada={self.portada}")
        # Borra archivos físicos antes de eliminar el objeto
        if self.archivo:
            logger.warning(f"[Libro.delete] Borrando archivo: {self.archivo.name}")
            self.archivo.delete(save=False)
        if self.portada:
            logger.warning(f"[Libro.delete] Borrando portada: {self.portada.name}")
            self.portada.delete(save=False)
        super().delete(*args, **kwargs)
        logger.warning(f"[Libro.delete] FIN")

    def __str__(self):
        return self.titulo