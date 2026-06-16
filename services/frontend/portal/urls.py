from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('portal/tramites/', views.mis_tramites, name='mis_tramites'),
    path('portal/tramites/nuevo/', views.crear_tramite, name='crear_tramite'),
    path('portal/tramites/<str:codigo>/', views.detalle_tramite, name='detalle_tramite'),
    path('portal/bandeja/', views.bandeja_tramites, name='bandeja_tramites'),
    path('portal/bodega/', views.inventario, name='inventario'),
    path('portal/bodega/solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('portal/bodega/solicitudes/nueva/', views.crear_solicitud, name='crear_solicitud'),
    path('portal/bodega/solicitudes/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('portal/bodega/analisis-ia/', views.analisis_ia, name='analisis_ia'),
]
