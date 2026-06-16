from django.urls import path
from . import views

app_name = 'analisis'

urlpatterns = [
    path('analisis-inventario/', views.analisis_inventario, name='analisis_inventario'),
]
