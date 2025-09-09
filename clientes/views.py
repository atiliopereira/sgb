from decimal import Decimal

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models

from liquidaciones.models import Liquidacion, Pago

from .models import Cliente
from .forms import ClienteForm


def estado_cuenta(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    liquidaciones = Liquidacion.objects.filter(cliente=cliente).select_related('proveedor__procedencia').prefetch_related('liquidacionitem_set').order_by("fecha")
    pagos = Pago.objects.filter(liquidacion__cliente=cliente).select_related('liquidacion', 'banco').order_by("fecha")

    # Create a comprehensive list combining liquidaciones and pagos
    account_entries = []

    # Add liquidaciones as debits
    for liquidacion in liquidaciones:
        account_entries.append(
            {
                "fecha": liquidacion.fecha,
                "tipo": "liquidacion",
                "factura": liquidacion.numero_factura_comercial,
                "origen": liquidacion.procedencia.nombre,
                "prof": liquidacion.numero_despacho,
                "oc": liquidacion.ad_valorem,
                "bco": "",
                "referencia": liquidacion.fecha.strftime("%y%m%d"),
                "pagos": Decimal("0"),
                "liquidacion": liquidacion.valor_total_calculado,
                "liquidacion_obj": liquidacion,
            }
        )

    # Add pagos as credits
    for pago in pagos:
        account_entries.append(
            {
                "fecha": pago.fecha,
                "tipo": "pago",
                "factura": "",
                "origen": "",
                "prof": pago.liquidacion.numero_despacho,  # Get numero_despacho from related liquidacion
                "oc": "",
                "bco": pago.banco.nombre[:3].upper(),
                "referencia": pago.referencia or pago.fecha.strftime("%y%m%d"),
                "pagos": pago.monto,
                "liquidacion": Decimal("0"),
                "pago_obj": pago,
            }
        )

    # Sort all entries by date
    account_entries.sort(key=lambda x: x["fecha"])

    # Calculate running balance and totals
    total_pagos = Decimal("0")
    total_liquidaciones = Decimal("0")
    running_balance = Decimal("0")

    for entry in account_entries:
        total_pagos += entry["pagos"]
        total_liquidaciones += entry["liquidacion"]
        running_balance += entry["pagos"] - entry["liquidacion"]
        entry["saldo"] = running_balance

    total_saldo = total_pagos - total_liquidaciones

    context = {
        "cliente": cliente,
        "account_entries": account_entries,
        "total_pagos": total_pagos,
        "total_liquidaciones": total_liquidaciones,
        "total_saldo": total_saldo,
    }

    return render(request, "clientes/estado_cuenta.html", context)


def cliente_list(request):
    clientes = Cliente.objects.all().order_by('nombre')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        clientes = clientes.filter(
            models.Q(nombre__icontains=search) |
            models.Q(ruc__icontains=search) |
            models.Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(clientes, 10)  # Show 10 clientes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'title': 'Lista de Clientes'
    }
    return render(request, 'clientes/cliente_list.html', context)


def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        
        if form.is_valid():
            try:
                cliente = form.save()
                messages.success(request, f'Cliente {cliente.nombre} creado exitosamente.')
                return redirect('clientes:cliente_list')
                
            except Exception as e:
                print(f"❌ ERROR DURING CLIENTE SAVE: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, 'Error al crear el cliente.')
        else:
            print("=== CLIENTE FORM VALIDATION FAILED ===")
            print("Form errors:", dict(form.errors))
            if form.errors:
                messages.error(request, f'Error en el formulario: {form.errors}')
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'title': 'Crear Cliente'
    }
    return render(request, 'clientes/cliente_form.html', context)


def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'clientes/cliente_detail.html', {'cliente': cliente})


def cliente_edit(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        
        if form.is_valid():
            try:
                cliente = form.save()
                messages.success(request, 'Cliente actualizado exitosamente.')
                return redirect('clientes:cliente_detail', pk=cliente.pk)
                
            except Exception as e:
                print(f"❌ ERROR DURING CLIENTE UPDATE: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, 'Error al actualizar el cliente.')
        else:
            print("=== CLIENTE FORM VALIDATION FAILED ===")
            print("Form errors:", dict(form.errors))
            if form.errors:
                messages.error(request, f'Error en el formulario: {form.errors}')
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'title': f'Editar Cliente {cliente.nombre}',
        'cliente': cliente,
        'is_edit': True
    }
    return render(request, 'clientes/cliente_form.html', context)


def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        nombre_cliente = cliente.nombre
        cliente.delete()
        messages.success(request, f'Cliente {nombre_cliente} eliminado exitosamente.')
        return redirect('clientes:cliente_list')
    
    context = {
        'cliente': cliente,
        'title': 'Eliminar Cliente'
    }
    return render(request, 'clientes/cliente_confirm_delete.html', context)
