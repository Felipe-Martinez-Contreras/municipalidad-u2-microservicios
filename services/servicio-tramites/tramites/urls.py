from django.urls import path
from . import views

app_name = 'tramites'

urlpatterns = [
    path('', views.tramites_view, name='lista_crear'),
    path('tipos/', views.tipos_tramite, name='tipos'),
    path('bandeja/', views.bandeja_funcionario, name='bandeja'),
    path('<str:codigo>/', views.detalle_tramite, name='detalle'),
    path('<str:codigo>/historial/', views.historial_tramite, name='historial'),
    path('<str:codigo>/documentos/', views.adjuntar_documento, name='adjuntar_documento'),
]
