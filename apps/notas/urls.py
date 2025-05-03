from django.urls import path
from apps.notas.views import NotaBulkImportView, ImportacionNotasListView, NotasPorImportacionListView, MisNotasAPIView

urlpatterns = [
    path('importar-notas/', NotaBulkImportView.as_view(), name='importar-notas'),
    path('importaciones/', ImportacionNotasListView.as_view(), name='importaciones-list'),
    path('notas-por-importacion/<int:importacion_id>/', NotasPorImportacionListView.as_view(), name='notas-por-importacion'),
    path('mis-notas/', MisNotasAPIView.as_view(), name='mis-notas'),
]