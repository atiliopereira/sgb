from django.urls import path
from . import views

urlpatterns = [
    # Item URLs
    path('', views.item_list, name='item_list'),
    path('crear/', views.item_create, name='item_create'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('<int:pk>/editar/', views.item_edit, name='item_edit'),
    path('<int:pk>/eliminar/', views.item_delete, name='item_delete'),
]