from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'

class IsSecretario(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'secretario'

class IsUsuario(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'usuario'
