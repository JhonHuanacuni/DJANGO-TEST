from django.apps import AppConfig


class EnlacesConfig(AppConfig):  # Corregir el nombre de la clase
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.enlaces'
    label = 'enlaces'  # Corregir el nombre de la etiqueta
