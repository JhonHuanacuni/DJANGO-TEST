# users/urls.py

from django.urls import path
from apps.users.views import CustomAuthToken, UsuarioActualAPIView, UsuarioListCreateAPIView, EditarUsuarioAPIView, EliminarUsuarioAPIView, GenerarCarnetAPIView, CambiarPasswordAPIView


urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('usuario-actual/', UsuarioActualAPIView.as_view(), name='usuario-actual'),
    path('usuarios/', UsuarioListCreateAPIView.as_view(), name='usuarios-list-create'),
    path('usuarios/<int:pk>/editar/', EditarUsuarioAPIView.as_view(), name='editar-usuario'),
    path('usuarios/<int:pk>/eliminar/', EliminarUsuarioAPIView.as_view(), name='eliminar-usuario'),
    path('usuarios/<int:pk>/carnet/', GenerarCarnetAPIView.as_view(), name='generar-carnet'),
    path('usuarios/cambiar-password/', CambiarPasswordAPIView.as_view(), name='cambiar-password'),
]

