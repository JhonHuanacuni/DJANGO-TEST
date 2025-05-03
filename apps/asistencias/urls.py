from django.urls import path
from apps.asistencias.views import AsistenciaCreateAPIView, AsistenciaListAPIView, AsistenciaPorSalonAPIView

urlpatterns = [
    path('', AsistenciaCreateAPIView.as_view(), name='asistencias'),
    path('listar/', AsistenciaListAPIView.as_view(), name='listar-asistencias'),
    path('salon/<int:salon_id>/', AsistenciaPorSalonAPIView.as_view(), name='asistencias-por-salon'),
]
