from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('registro/', views.registro_ciudadano, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('verificar/', views.verificar_token, name='verificar_token'),
    path('funcionarios/crear/', views.crear_funcionario, name='crear_funcionario'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
]
