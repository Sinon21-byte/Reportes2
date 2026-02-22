from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('formulario/', views.formulario_view, name='formulario'),
    path('actividades/', views.actividades_view, name='actividades'),
]