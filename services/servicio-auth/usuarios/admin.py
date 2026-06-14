from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['email', 'rut', 'first_name', 'last_name', 'rol', 'departamento', 'is_active']
    list_filter = ['rol', 'departamento', 'is_active']
    search_fields = ['email', 'rut', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('Datos Municipales', {
            'fields': ('rol', 'departamento', 'rut', 'telefono')
        }),
    )
