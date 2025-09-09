from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Cliente CRUD URLs
    path('', views.cliente_list, name='cliente_list'),
    path('crear/', views.cliente_create, name='cliente_create'),
    path('<int:pk>/', views.cliente_detail, name='cliente_detail'),
    path('<int:pk>/editar/', views.cliente_edit, name='cliente_edit'),
    path('<int:pk>/eliminar/', views.cliente_delete, name='cliente_delete'),
    
    # Estado de cuenta URL
    path('estado-cuenta/<int:cliente_id>/', views.estado_cuenta, name='estado_cuenta'),
]