from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.users.models import Usuario

class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ['username', 'email', 'rol', 'is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets + (
        ('Rol personalizado', {'fields': ('rol',)}),
    )

admin.site.register(Usuario, UsuarioAdmin)