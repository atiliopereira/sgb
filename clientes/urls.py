from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('estado-cuenta/<int:cliente_id>/', views.estado_cuenta, name='estado_cuenta'),
]