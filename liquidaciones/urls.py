from django.urls import path

from . import views

urlpatterns = [
    # Liquidacion URLs
    path("", views.liquidacion_list, name="liquidacion_list"),
    path("crear/", views.liquidacion_create, name="liquidacion_create"),
    path("<int:pk>/", views.liquidacion_detail, name="liquidacion_detail"),
    path("<int:pk>/editar/", views.liquidacion_edit, name="liquidacion_edit"),
    path("<int:pk>/eliminar/", views.liquidacion_delete, name="liquidacion_delete"),
    # Pago URLs
    path("pagos/", views.pago_list, name="pago_list"),
    path("pagos/crear/", views.pago_create, name="pago_create"),
    path("pagos/<int:pk>/", views.pago_detail, name="pago_detail"),
    path("pagos/<int:pk>/editar/", views.pago_edit, name="pago_edit"),
    path("pagos/<int:pk>/eliminar/", views.pago_delete, name="pago_delete"),
    # Banco URLs
    path("bancos/", views.banco_list, name="banco_list"),
    path("bancos/crear/", views.banco_create, name="banco_create"),
    path("bancos/<int:pk>/", views.banco_detail, name="banco_detail"),
    path("bancos/<int:pk>/editar/", views.banco_edit, name="banco_edit"),
    path("bancos/<int:pk>/eliminar/", views.banco_delete, name="banco_delete"),
    # Proveedor URLs
    path("proveedores/", views.proveedor_list, name="proveedor_list"),
    path("proveedores/crear/", views.proveedor_create, name="proveedor_create"),
    path("proveedores/<int:pk>/", views.proveedor_detail, name="proveedor_detail"),
    path("proveedores/<int:pk>/editar/", views.proveedor_edit, name="proveedor_edit"),
    path(
        "proveedores/<int:pk>/eliminar/",
        views.proveedor_delete,
        name="proveedor_delete",
    ),
    # Procedencia URLs
    path("procedencias/", views.procedencia_list, name="procedencia_list"),
    path("procedencias/crear/", views.procedencia_create, name="procedencia_create"),
    path("procedencias/<int:pk>/", views.procedencia_detail, name="procedencia_detail"),
    path(
        "procedencias/<int:pk>/editar/", views.procedencia_edit, name="procedencia_edit"
    ),
    path(
        "procedencias/<int:pk>/eliminar/",
        views.procedencia_delete,
        name="procedencia_delete",
    ),
    # PlanillaGastos URLs
    path("planillas-gastos/", views.planilla_gastos_list, name="planilla_gastos_list"),
    path(
        "planillas-gastos/crear/",
        views.planilla_gastos_create,
        name="planilla_gastos_create",
    ),
    path(
        "planillas-gastos/<int:pk>/",
        views.planilla_gastos_detail,
        name="planilla_gastos_detail",
    ),
    path(
        "planillas-gastos/<int:pk>/editar/",
        views.planilla_gastos_edit,
        name="planilla_gastos_edit",
    ),
    path(
        "planillas-gastos/<int:pk>/eliminar/",
        views.planilla_gastos_delete,
        name="planilla_gastos_delete",
    ),
    # API URLs
    path("api/item-autocomplete/", views.item_autocomplete, name="item_autocomplete"),
    path(
        "api/cliente-autocomplete/",
        views.cliente_autocomplete,
        name="cliente_autocomplete",
    ),
    path(
        "api/proveedor-autocomplete/",
        views.proveedor_autocomplete,
        name="proveedor_autocomplete",
    ),
    path(
        "api/liquidacion-autocomplete/",
        views.liquidacion_autocomplete,
        name="liquidacion_autocomplete",
    ),
    path(
        "api/planilla-gastos-autocomplete/",
        views.planilla_gastos_autocomplete,
        name="planilla_gastos_autocomplete",
    ),
]
