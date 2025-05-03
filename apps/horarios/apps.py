from django.apps import AppConfig


class HorariosConfig(AppConfig):  # Corregir el nombre de la clase
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.horarios'
    label = 'horarios'  # Corregir el nombre de la etiqueta
