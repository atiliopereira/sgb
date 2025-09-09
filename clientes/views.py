from decimal import Decimal

from django.shortcuts import get_object_or_404, render

from liquidaciones.models import Liquidacion, Pago

from .models import Cliente


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
