from django.urls import path
from apps.membresias.views import (
    MembresiaListCreateAPIView,
    MembresiaRetrieveUpdateDeleteAPIView,
    PagoMembresiaCreateAPIView,
    PagosListAPIView,
    PagosPorMembresiaAPIView,
    SalonRemoveUserView,
    SalonViewSet,
    SalonDetailView,
    SalonPublicViewSet
)

urlpatterns = [
    path('', MembresiaListCreateAPIView.as_view(), name='membresias-list-create'),
    path('<int:pk>/', MembresiaRetrieveUpdateDeleteAPIView.as_view(), name='membresias-detail'),
    
    # Pagos
    path('pagos/lista/', PagosListAPIView.as_view(), name='lista-pagos'),
    path('pagos/<int:membresia_id>/', PagosPorMembresiaAPIView.as_view(), name='pagos-de-membresia'),
    path('pagos/', PagoMembresiaCreateAPIView.as_view(), name='registrar-pago'),
    
    #salones
    path('salones/', SalonViewSet.as_view(), name='salon-list'),
    path('salones/<int:pk>/', SalonDetailView.as_view(), name='salon-detail'),
    path('salones/<int:pk>/remove_user/', SalonRemoveUserView.as_view(), name='salon-remove-user'),
    path('salones/public/', SalonPublicViewSet.as_view(), name='salon-public-list')
]