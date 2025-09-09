from django.urls import path
from . import views

urlpatterns = [
    # Liquidacion URLs
    path('', views.liquidacion_list, name='liquidacion_list'),
    path('crear/', views.liquidacion_create, name='liquidacion_create'),
    path('<int:pk>/', views.liquidacion_detail, name='liquidacion_detail'),
    path('<int:pk>/editar/', views.liquidacion_edit, name='liquidacion_edit'),
    path('<int:pk>/eliminar/', views.liquidacion_delete, name='liquidacion_delete'),
    
    # Pago URLs
    path('pagos/', views.pago_list, name='pago_list'),
    path('pagos/crear/', views.pago_create, name='pago_create'),
    path('pagos/<int:pk>/', views.pago_detail, name='pago_detail'),
    path('pagos/<int:pk>/editar/', views.pago_edit, name='pago_edit'),
    path('pagos/<int:pk>/eliminar/', views.pago_delete, name='pago_delete'),
    
    # API URLs
    path('api/item-autocomplete/', views.item_autocomplete, name='item_autocomplete'),
    path('api/cliente-autocomplete/', views.cliente_autocomplete, name='cliente_autocomplete'),
    path('api/proveedor-autocomplete/', views.proveedor_autocomplete, name='proveedor_autocomplete'),
    path('api/liquidacion-autocomplete/', views.liquidacion_autocomplete, name='liquidacion_autocomplete'),
]