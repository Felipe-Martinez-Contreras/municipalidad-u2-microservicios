from django.contrib import admin
from .models import Tramite, TipoTramite, DocumentoTramite, HistorialTramite

@admin.register(TipoTramite)
class TipoTramiteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'requiere_documentos', 'departamento_responsable']
    list_filter = ['activo', 'departamento_responsable']

@admin.register(Tramite)
class TramiteAdmin(admin.ModelAdmin):
    list_display = ['codigo_seguimiento', 'tipo', 'estado', 'ciudadano_nombre', 'creado_en']
    list_filter = ['estado', 'tipo']
    search_fields = ['codigo_seguimiento', 'ciudadano_rut', 'ciudadano_email']
