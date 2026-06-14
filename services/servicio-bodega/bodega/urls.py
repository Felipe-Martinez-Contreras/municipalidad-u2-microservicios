from django.urls import path
from . import views

app_name = 'bodega'

urlpatterns = [
    path('categorias/', views.categorias, name='categorias'),
    path('inventario/', views.inventario, name='inventario'),
    path('inventario/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('solicitudes/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('solicitudes/<int:solicitud_id>/productos/', views.agregar_producto_solicitud, name='agregar_producto'),
]
