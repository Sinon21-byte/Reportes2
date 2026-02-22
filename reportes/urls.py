from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('formulario/', views.formulario_view, name='formulario'),
    path('actividades/', views.actividades_view, name='actividades'),
]

# Esto sirve MEDIA_URL durante el DEBUG para que InlineImage funcione
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
