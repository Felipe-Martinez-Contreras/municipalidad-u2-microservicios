from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('auth-admin/', admin.site.urls),
    path('api/auth/', include('usuarios.urls')),
]
