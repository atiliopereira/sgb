from django.urls import path
from . import views

urlpatterns = [
    path('', views.liquidacion_list, name='liquidacion_list'),
    path('crear/', views.liquidacion_create, name='liquidacion_create'),
    path('<int:pk>/', views.liquidacion_detail, name='liquidacion_detail'),
    path('<int:pk>/editar/', views.liquidacion_edit, name='liquidacion_edit'),
    path('<int:pk>/eliminar/', views.liquidacion_delete, name='liquidacion_delete'),
    path('api/item-autocomplete/', views.item_autocomplete, name='item_autocomplete'),
    path('api/cliente-autocomplete/', views.cliente_autocomplete, name='cliente_autocomplete'),
    path('api/proveedor-autocomplete/', views.proveedor_autocomplete, name='proveedor_autocomplete'),
]