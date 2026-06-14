from django.contrib import admin
from .models import Producto, CategoriaProducto, MovimientoStock, SolicitudBodega, DetalleSolicitud


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'creado_en']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'stock_actual', 'stock_minimo', 'activo']
    list_filter = ['activo', 'categoria', 'unidad_medida']
    search_fields = ['codigo', 'nombre']


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'stock_resultante', 'usuario_nombre', 'fecha']
    list_filter = ['tipo']
    search_fields = ['producto__nombre', 'usuario_nombre']


@admin.register(SolicitudBodega)
class SolicitudBodegaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'departamento_solicitante', 'estado', 'solicitante_nombre', 'creado_en']
    list_filter = ['estado', 'departamento_solicitante']
    search_fields = ['codigo', 'solicitante_nombre', 'solicitante_email']
