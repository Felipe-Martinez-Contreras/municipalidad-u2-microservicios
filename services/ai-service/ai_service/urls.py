from django.urls import path, include

urlpatterns = [
    path('ai/', include('analisis.urls')),
]
