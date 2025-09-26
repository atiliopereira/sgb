from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from clientes.models import Cliente
from items.models import Item
from liquidaciones.models import Liquidacion, Procedencia, Proveedor, Banco, Pago


@login_required
def dashboard(request):
    context = {
        'stats': {
            'users': User.objects.count(),
            'clientes': Cliente.objects.count(),
            'items': Item.objects.count(),
            'liquidaciones': Liquidacion.objects.count(),
            'procedencias': Procedencia.objects.count(),
            'proveedores': Proveedor.objects.count(),
            'bancos': Banco.objects.count(),
            'pagos': Pago.objects.count(),
        }
    }
    return render(request, 'dashboard.html', context)