from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from clientes.models import Cliente
from items.models import Item

from .forms import LiquidacionForm, LiquidacionItemFormSet, PagoForm, BancoForm, ProcedenciaForm, ProveedorForm, PlanillaGastosForm, PlanillaGastosItemFormSet
from .models import Banco, Liquidacion, LiquidacionItem, Pago, Proveedor, Procedencia, PlanillaGastos, PlanillaGastosItem


def liquidacion_create(request):
    print("=== LIQUIDACION CREATE VIEW CALLED ===")
    print("Request method:", request.method)

    if request.method == "POST":
        print("=== POST REQUEST RECEIVED ===")
        print("POST data keys:", list(request.POST.keys()))
        print(
            "POST data values:",
            {k: v for k, v in request.POST.items() if k != "csrfmiddlewaretoken"},
        )

        form = LiquidacionForm(request.POST)
        formset = LiquidacionItemFormSet(request.POST)

        print("Form valid:", form.is_valid())
        if not form.is_valid():
            print("Form errors:", dict(form.errors))

        print("Formset valid:", formset.is_valid())
        if not formset.is_valid():
            print("Formset errors:", [dict(form.errors) for form in formset])
            print("Formset non_form_errors:", formset.non_form_errors())

        if form.is_valid() and formset.is_valid():
            print("=== BOTH FORMS VALID - SAVING ===")
            try:
                liquidacion = form.save()
                print(f"✅ Liquidacion saved with ID: {liquidacion.id}")

                # Only save forms that have an item selected
                instances = formset.save(commit=False)
                saved_items = []

                for instance in instances:
                    # Check if item_id exists instead of accessing the item object
                    if instance.item_id:  # Only save if item is selected
                        instance.liquidacion = liquidacion
                        # Ensure numeric fields have default values if empty
                        if not instance.retencion:
                            instance.retencion = 0
                        if not instance.monto:
                            instance.monto = 0
                        if not instance.iva:
                            instance.iva = 0
                        instance.save()
                        saved_items.append(instance)
                        print(f"✅ Saved item: {instance.item}")

                # Also handle formset deletions
                for obj in formset.deleted_objects:
                    obj.delete()

                # Show appropriate message
                if saved_items:
                    messages.success(
                        request,
                        f"Liquidación {liquidacion.numero_liquidacion} creada exitosamente con {len(saved_items)} item(s).",
                    )
                else:
                    messages.success(
                        request,
                        f"Liquidación {liquidacion.numero_liquidacion} creada exitosamente.",
                    )
                    messages.info(
                        request,
                        "No se agregaron items a esta liquidación. Puedes editarla para agregar items más tarde.",
                    )

                print("=== REDIRECTING TO LIQUIDACION_LIST ===")
                redirect_response = redirect("liquidacion_list")
                print(f"Redirect response: {redirect_response}")
                print(f"Redirect URL: {redirect_response.url}")
                return redirect_response

            except Exception as e:
                print(f"❌ ERROR DURING SAVE: {e}")
                import traceback

                traceback.print_exc()
        else:
            print("=== FORM VALIDATION FAILED ===")
            # Add error messages for debugging
            if not form.is_valid():
                messages.error(
                    request, f"Error en el formulario principal: {form.errors}"
                )
            if not formset.is_valid():
                messages.error(request, f"Error en los items: {formset.errors}")

            # Preserve formset data for re-rendering
            for form_instance in formset:
                if (
                    hasattr(form_instance, "cleaned_data")
                    and form_instance.cleaned_data
                    and form_instance.cleaned_data.get("item")
                ):
                    # Ensure item data is preserved in the form
                    form_instance.initial["item"] = form_instance.cleaned_data[
                        "item"
                    ].id
    else:
        print("=== GET REQUEST - RENDERING EMPTY FORM ===")
        form = LiquidacionForm()
        # For create, we want one empty form to start with
        formset = LiquidacionItemFormSet(queryset=LiquidacionItem.objects.none())
        formset.extra = 1

    context = {"form": form, "formset": formset, "title": "Crear Liquidación"}
    return render(request, "liquidaciones/liquidacion_form.html", context)


def liquidacion_detail(request, pk):
    liquidacion = get_object_or_404(Liquidacion, pk=pk)
    return render(
        request, "liquidaciones/liquidacion_detail.html", {"liquidacion": liquidacion}
    )


def liquidacion_edit(request, pk):
    print(f"=== LIQUIDACION EDIT VIEW CALLED (PK: {pk}) ===")
    print("Request method:", request.method)

    liquidacion = get_object_or_404(Liquidacion, pk=pk)

    if request.method == "POST":
        print("=== POST REQUEST RECEIVED FOR EDIT ===")
        print("POST data keys:", list(request.POST.keys()))
        print(
            "POST data values:",
            {k: v for k, v in request.POST.items() if k != "csrfmiddlewaretoken"},
        )

        form = LiquidacionForm(request.POST, instance=liquidacion)
        formset = LiquidacionItemFormSet(request.POST, instance=liquidacion)

        print("Form valid:", form.is_valid())
        if not form.is_valid():
            print("Form errors:", dict(form.errors))

        print("Formset valid:", formset.is_valid())
        if not formset.is_valid():
            print("Formset errors:", [dict(form.errors) for form in formset])
            print("Formset non_form_errors:", formset.non_form_errors())

        if form.is_valid() and formset.is_valid():
            print("=== BOTH FORMS VALID - UPDATING ===")
            try:
                liquidacion = form.save()
                print(f"✅ Liquidacion updated with ID: {liquidacion.id}")

                # Only save non-empty forms
                instances = formset.save(commit=False)
                saved_items = []
                for instance in instances:
                    # Check if item_id exists instead of accessing the item object
                    if instance.item_id:  # Only save if item is selected
                        # Ensure numeric fields have default values if empty
                        if not instance.retencion:
                            instance.retencion = 0
                        if not instance.monto:
                            instance.monto = 0
                        if not instance.iva:
                            instance.iva = 0
                        instance.save()
                        saved_items.append(instance)
                        print(f"✅ Updated item: {instance.item}")

                # Delete items marked for deletion
                print(f"Items marked for deletion: {len(formset.deleted_objects)}")
                for i, obj in enumerate(formset.deleted_objects):
                    print(f"Deleting item {i}: {obj.descripcion} - {obj.monto}")
                    obj.delete()
                    print(f"✅ Deleted item: {obj}")

                messages.success(request, "Liquidación actualizada exitosamente.")
                print("=== REDIRECTING TO LIQUIDACION_DETAIL ===")
                redirect_response = redirect("liquidacion_detail", pk=liquidacion.pk)
                print(f"Redirect response: {redirect_response}")
                print(f"Redirect URL: {redirect_response.url}")
                return redirect_response

            except Exception as e:
                print(f"❌ ERROR DURING UPDATE: {e}")
                import traceback

                traceback.print_exc()
        else:
            print("=== FORM VALIDATION FAILED ===")
            # Add error messages for debugging
            if not form.is_valid():
                messages.error(
                    request, f"Error en el formulario principal: {form.errors}"
                )
            if not formset.is_valid():
                messages.error(request, f"Error en los items: {formset.errors}")

            # Preserve formset data for re-rendering
            for form_instance in formset:
                if (
                    hasattr(form_instance, "cleaned_data")
                    and form_instance.cleaned_data
                    and form_instance.cleaned_data.get("item")
                ):
                    # Ensure item data is preserved in the form
                    form_instance.initial["item"] = form_instance.cleaned_data[
                        "item"
                    ].id
    else:
        form = LiquidacionForm(instance=liquidacion)
        # For edit, only show existing items, no extra forms
        formset = LiquidacionItemFormSet(instance=liquidacion)
        formset.extra = 0

    context = {
        "form": form,
        "formset": formset,
        "title": f"Editar Liquidación {liquidacion.numero_liquidacion}",
        "liquidacion": liquidacion,
        "is_edit": True,
    }
    return render(request, "liquidaciones/liquidacion_form.html", context)


def liquidacion_delete(request, pk):
    liquidacion = get_object_or_404(Liquidacion, pk=pk)

    if request.method == "POST":
        numero_liquidacion = liquidacion.numero_liquidacion
        liquidacion.delete()
        messages.success(
            request, f"Liquidación {numero_liquidacion} eliminada exitosamente."
        )
        return redirect("liquidacion_list")

    context = {"liquidacion": liquidacion, "title": "Eliminar Liquidación"}
    return render(request, "liquidaciones/liquidacion_confirm_delete.html", context)


def liquidacion_list(request):
    liquidaciones = Liquidacion.objects.all().order_by("-fecha")

    # Search functionality
    search = request.GET.get("search", "")
    if search:
        liquidaciones = liquidaciones.filter(
            models.Q(numero_liquidacion__icontains=search)
            | models.Q(cliente__nombre__icontains=search)
            | models.Q(numero_despacho__icontains=search)
        )

    # Pagination
    paginator = Paginator(liquidaciones, 10)  # Show 10 liquidaciones per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
        "title": "Lista de Liquidaciones",
    }
    return render(request, "liquidaciones/liquidacion_list.html", context)


def item_autocomplete(request):
    query = request.GET.get("q", "")
    item_id = request.GET.get("id", "")

    if item_id:
        # Fetch specific item by ID for restoration after form errors
        try:
            item = Item.objects.get(id=item_id)
            results = [{"id": item.id, "text": item.descripcion}]
        except Item.DoesNotExist:
            results = []
    elif query:
        items = Item.objects.filter(descripcion__icontains=query)[:10]
        results = [{"id": item.id, "text": item.descripcion} for item in items]
    else:
        results = []

    return JsonResponse({"results": results})


def pago_create(request):
    if request.method == "POST":
        form = PagoForm(request.POST)

        if form.is_valid():
            try:
                pago = form.save()
                messages.success(
                    request, f"Pago {pago.numero_despacho} creado exitosamente."
                )
                return redirect("pago_list")

            except Exception as e:
                print(f"❌ ERROR DURING PAGO SAVE: {e}")
                import traceback

                traceback.print_exc()
        else:
            print("=== PAGO FORM VALIDATION FAILED ===")
            print("Form errors:", dict(form.errors))
            if form.errors:
                messages.error(request, f"Error en el formulario: {form.errors}")
    else:
        form = PagoForm()

    context = {"form": form, "title": "Crear Pago"}
    return render(request, "liquidaciones/pago_form.html", context)


def pago_list(request):
    pagos = Pago.objects.select_related("liquidacion__cliente", "banco").order_by(
        "-fecha"
    )

    # Search functionality
    search = request.GET.get("search", "")
    if search:
        pagos = pagos.filter(
            models.Q(liquidacion__numero_despacho__icontains=search)
            | models.Q(liquidacion__cliente__nombre__icontains=search)
            | models.Q(banco__nombre__icontains=search)
            | models.Q(referencia__icontains=search)
        )

    # Pagination
    paginator = Paginator(pagos, 10)  # Show 10 pagos per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj, "search": search, "title": "Lista de Pagos"}
    return render(request, "liquidaciones/pago_list.html", context)


def pago_detail(request, pk):
    pago = get_object_or_404(
        Pago.objects.select_related("liquidacion__cliente", "banco"), pk=pk
    )
    return render(request, "liquidaciones/pago_detail.html", {"pago": pago})


def pago_edit(request, pk):
    pago = get_object_or_404(
        Pago.objects.select_related("liquidacion__cliente", "banco"), pk=pk
    )

    if request.method == "POST":
        form = PagoForm(request.POST, instance=pago)

        if form.is_valid():
            try:
                pago = form.save()
                messages.success(request, "Pago actualizado exitosamente.")
                return redirect("pago_detail", pk=pago.pk)

            except Exception as e:
                print(f"❌ ERROR DURING PAGO UPDATE: {e}")
                import traceback

                traceback.print_exc()
        else:
            print("=== PAGO FORM VALIDATION FAILED ===")
            print("Form errors:", dict(form.errors))
            if form.errors:
                messages.error(request, f"Error en el formulario: {form.errors}")
    else:
        form = PagoForm(instance=pago)

    context = {
        "form": form,
        "title": f"Editar Pago {pago.numero_despacho}",
        "pago": pago,
        "is_edit": True,
    }
    return render(request, "liquidaciones/pago_form.html", context)


def pago_delete(request, pk):
    pago = get_object_or_404(
        Pago.objects.select_related("liquidacion__cliente", "banco"), pk=pk
    )

    if request.method == "POST":
        numero_despacho = pago.numero_despacho
        pago.delete()
        messages.success(request, f"Pago {numero_despacho} eliminado exitosamente.")
        return redirect("pago_list")

    context = {"pago": pago, "title": "Eliminar Pago"}
    return render(request, "liquidaciones/pago_confirm_delete.html", context)


def cliente_autocomplete(request):
    query = request.GET.get("q", "")
    if query:
        clientes = Cliente.objects.filter(nombre__icontains=query)[:10]
        results = [{"id": cliente.id, "text": cliente.nombre} for cliente in clientes]
    else:
        results = []

    return JsonResponse({"results": results})


def pago_create(request):
    if request.method == "POST":
        form = PagoForm(request.POST)

        if form.is_valid():
            try:
                pago = form.save()
                messages.success(
                    request, f"Pago {pago.numero_despacho} creado exitosamente."
                )
                return redirect("pago_list")

            except Exception as e:
                print(f"❌ ERROR DURING PAGO SAVE: {e}")
                import traceback

                traceback.print_exc()
        else:
            print("=== PAGO FORM VALIDATION FAILED ===")
            print("Form errors:", dict(form.errors))
            if form.errors:
                messages.error(request, f"Error en el formulario: {form.errors}")
    else:
        form = PagoForm()

    context = {"form": form, "title": "Crear Pago"}
    return render(request, "liquidaciones/pago_form.html", context)


def pago_list(request):
    pagos = Pago.objects.select_related("liquidacion__cliente", "banco").order_by(
        "-fecha"
    )

    # Search functionality
    search = request.GET.get("search", "")
    if search:
        pagos = pagos.filter(
            models.Q(liquidacion__numero_despacho__icontains=search)
            | models.Q(liquidacion__cliente__nombre__icontains=search)
            | models.Q(banco__nombre__icontains=search)
            | models.Q(referencia__icontains=search)
        )

    # Pagination
    paginator = Paginator(pagos, 10)  # Show 10 pagos per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj, "search": search, "title": "Lista de Pagos"}
    return render(request, "liquidaciones/pago_list.html", context)


def pago_detail(request, pk):
    pago = get_object_or_404(
        Pago.objects.select_related("liquidacion__cliente", "banco"), pk=pk
    )
    return render(request, "liquidaciones/pago_detail.html", {"pago": pago})


def pago_edit(request, pk):
    pago = get_object_or_404(
        Pago.objects.select_related("liquidacion__cliente", "banco"), pk=pk
    )

    if request.method == "POST":
        form = PagoForm(request.POST, instance=pago)

        if form.is_valid():
            try:
                pago = form.save()
                messages.success(request, "Pago actualizado exitosamente.")
                return redirect("pago_detail", pk=pago.pk)

            except Exception as e:
                print(f"❌ ERROR DURING PAGO UPDATE: {e}")
                import traceback

                traceback.print_exc()
        else:
            print("=== PAGO FORM VALIDATION FAILED ===")
            print("Form errors:", dict(form.errors))
            if form.errors:
                messages.error(request, f"Error en el formulario: {form.errors}")
    else:
        form = PagoForm(instance=pago)

    context = {
        "form": form,
        "title": f"Editar Pago {pago.numero_despacho}",
        "pago": pago,
        "is_edit": True,
    }
    return render(request, "liquidaciones/pago_form.html", context)


def pago_delete(request, pk):
    pago = get_object_or_404(
        Pago.objects.select_related("liquidacion__cliente", "banco"), pk=pk
    )

    if request.method == "POST":
        numero_despacho = pago.numero_despacho
        pago.delete()
        messages.success(request, f"Pago {numero_despacho} eliminado exitosamente.")
        return redirect("pago_list")

    context = {"pago": pago, "title": "Eliminar Pago"}
    return render(request, "liquidaciones/pago_confirm_delete.html", context)


def proveedor_autocomplete(request):
    query = request.GET.get("q", "")
    if query:
        proveedores = Proveedor.objects.select_related("procedencia").filter(
            models.Q(nombre__icontains=query)
            | models.Q(procedencia__nombre__icontains=query)
        )[:10]

        results = []
        for proveedor in proveedores:
            procedencia_nombre = (
                proveedor.procedencia.nombre
                if proveedor.procedencia
                else "Sin especificar"
            )
            results.append(
                {
                    "id": proveedor.id,
                    "text": f"{proveedor.nombre} ({procedencia_nombre})",
                }
            )
    else:
        results = []

    return JsonResponse({"results": results})


def liquidacion_autocomplete(request):
    query = request.GET.get("q", "")
    liquidacion_id = request.GET.get("id", "")

    def format_amount(amount):
        """Format amount with thousand separators and no decimals"""
        return f"{int(amount):,}".replace(',', '.')
    
    if liquidacion_id:
        # Fetch specific liquidacion by ID for restoration after form errors
        try:
            liquidacion = Liquidacion.objects.select_related("cliente").get(
                id=liquidacion_id
            )
            formatted_amount = format_amount(liquidacion.valor_total_calculado)
            results = [
                {
                    "id": liquidacion.id,
                    "text": f"{liquidacion.numero_despacho} - {liquidacion.cliente.nombre}: {formatted_amount}",
                }
            ]
        except Liquidacion.DoesNotExist:
            results = []
    elif query:
        liquidaciones = Liquidacion.objects.select_related("cliente").filter(
            models.Q(numero_despacho__icontains=query)
            | models.Q(cliente__nombre__icontains=query)
        )[:10]
        results = [
            {
                "id": liq.id,
                "text": f"{liq.numero_despacho} - {liq.cliente.nombre}: {format_amount(liq.valor_total_calculado)}",
            }
            for liq in liquidaciones
        ]
    else:
        results = []

    return JsonResponse({"results": results})


def pago_create(request):
    if request.method == "POST":
        form = PagoForm(request.POST)

        if form.is_valid():
            try:
                pago = form.save()
                messages.success(
                    request, f"Pago {pago.numero_despacho} creado exitosamente."
                )
                return redirect("pago_list")

            except Exception as e:
                print(f"❌ ERROR DURING PAGO SAVE: {e}")
                import traceback

                traceback.print_exc()
        else:
            print("=== PAGO FORM VALIDATION FAILED ===")
            print("Form errors:", dict(form.errors))
            if form.errors:
                messages.error(request, f"Error en el formulario: {form.errors}")
    else:
        form = PagoForm()

    context = {"form": form, "title": "Crear Pago"}
    return render(request, "liquidaciones/pago_form.html", context)


def pago_list(request):
    pagos = Pago.objects.select_related("liquidacion__cliente", "banco").order_by(
        "-fecha"
    )

    # Search functionality
    search = request.GET.get("search", "")
    if search:
        pagos = pagos.filter(
            models.Q(liquidacion__numero_despacho__icontains=search)
            | models.Q(liquidacion__cliente__nombre__icontains=search)
            | models.Q(banco__nombre__icontains=search)
            | models.Q(referencia__icontains=search)
        )

    # Pagination
    paginator = Paginator(pagos, 10)  # Show 10 pagos per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj, "search": search, "title": "Lista de Pagos"}
    return render(request, "liquidaciones/pago_list.html", context)


def pago_detail(request, pk):
    pago = get_object_or_404(
        Pago.objects.select_related("liquidacion__cliente", "banco"), pk=pk
    )
    return render(request, "liquidaciones/pago_detail.html", {"pago": pago})


def pago_edit(request, pk):
    pago = get_object_or_404(
        Pago.objects.select_related("liquidacion__cliente", "banco"), pk=pk
    )

    if request.method == "POST":
        form = PagoForm(request.POST, instance=pago)

        if form.is_valid():
            try:
                pago = form.save()
                messages.success(request, "Pago actualizado exitosamente.")
                return redirect("pago_detail", pk=pago.pk)

            except Exception as e:
                print(f"❌ ERROR DURING PAGO UPDATE: {e}")
                import traceback

                traceback.print_exc()
        else:
            print("=== PAGO FORM VALIDATION FAILED ===")
            print("Form errors:", dict(form.errors))
            if form.errors:
                messages.error(request, f"Error en el formulario: {form.errors}")
    else:
        form = PagoForm(instance=pago)

    context = {
        "form": form,
        "title": f"Editar Pago {pago.numero_despacho}",
        "pago": pago,
        "is_edit": True,
    }
    return render(request, "liquidaciones/pago_form.html", context)


def pago_delete(request, pk):
    pago = get_object_or_404(
        Pago.objects.select_related("liquidacion__cliente", "banco"), pk=pk
    )

    if request.method == "POST":
        numero_despacho = pago.numero_despacho
        pago.delete()
        messages.success(request, f"Pago {numero_despacho} eliminado exitosamente.")
        return redirect("pago_list")

    context = {"pago": pago, "title": "Eliminar Pago"}
    return render(request, "liquidaciones/pago_confirm_delete.html", context)


# Banco CRUD Views
def banco_list(request):
    bancos = Banco.objects.all().order_by("nombre")
    
    # Search functionality
    search = request.GET.get("search", "")
    if search:
        bancos = bancos.filter(
            models.Q(nombre__icontains=search) |
            models.Q(titular__icontains=search) |
            models.Q(numero_cuenta__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(bancos, 10)  # Show 10 bancos per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
        "title": "Lista de Bancos"
    }
    return render(request, "liquidaciones/banco_list.html", context)


def banco_create(request):
    if request.method == "POST":
        form = BancoForm(request.POST)
        
        if form.is_valid():
            try:
                banco = form.save()
                messages.success(request, f"Banco {banco.nombre} creado exitosamente.")
                return redirect("banco_list")
            except Exception as e:
                messages.error(request, f"Error al crear el banco: {e}")
        else:
            messages.error(request, "Error en el formulario. Por favor corrige los errores.")
    else:
        form = BancoForm()
    
    context = {"form": form, "title": "Crear Banco"}
    return render(request, "liquidaciones/banco_form.html", context)


def banco_detail(request, pk):
    banco = get_object_or_404(Banco, pk=pk)
    return render(request, "liquidaciones/banco_detail.html", {"banco": banco})


def banco_edit(request, pk):
    banco = get_object_or_404(Banco, pk=pk)
    
    if request.method == "POST":
        form = BancoForm(request.POST, instance=banco)
        
        if form.is_valid():
            try:
                banco = form.save()
                messages.success(request, "Banco actualizado exitosamente.")
                return redirect("banco_detail", pk=banco.pk)
            except Exception as e:
                messages.error(request, f"Error al actualizar el banco: {e}")
        else:
            messages.error(request, "Error en el formulario. Por favor corrige los errores.")
    else:
        form = BancoForm(instance=banco)
    
    context = {
        "form": form,
        "title": f"Editar Banco {banco.nombre}",
        "banco": banco,
        "is_edit": True
    }
    return render(request, "liquidaciones/banco_form.html", context)


def banco_delete(request, pk):
    banco = get_object_or_404(Banco, pk=pk)
    
    if request.method == "POST":
        nombre = banco.nombre
        banco.delete()
        messages.success(request, f"Banco {nombre} eliminado exitosamente.")
        return redirect("banco_list")
    
    context = {"banco": banco, "title": "Eliminar Banco"}
    return render(request, "liquidaciones/banco_confirm_delete.html", context)


# Proveedor CRUD Views
def proveedor_list(request):
    proveedores = Proveedor.objects.select_related("procedencia").order_by("nombre")
    
    # Search functionality
    search = request.GET.get("search", "")
    if search:
        proveedores = proveedores.filter(
            models.Q(nombre__icontains=search) |
            models.Q(procedencia__nombre__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(proveedores, 10)  # Show 10 proveedores per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
        "title": "Lista de Proveedores"
    }
    return render(request, "liquidaciones/proveedor_list.html", context)


def proveedor_create(request):
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        
        if form.is_valid():
            try:
                proveedor = form.save()
                messages.success(request, f"Proveedor {proveedor.nombre} creado exitosamente.")
                return redirect("proveedor_list")
            except Exception as e:
                messages.error(request, f"Error al crear el proveedor: {e}")
        else:
            messages.error(request, "Error en el formulario. Por favor corrige los errores.")
    else:
        form = ProveedorForm()
    
    context = {"form": form, "title": "Crear Proveedor"}
    return render(request, "liquidaciones/proveedor_form.html", context)


def proveedor_detail(request, pk):
    proveedor = get_object_or_404(Proveedor.objects.select_related("procedencia"), pk=pk)
    return render(request, "liquidaciones/proveedor_detail.html", {"proveedor": proveedor})


def proveedor_edit(request, pk):
    proveedor = get_object_or_404(Proveedor.objects.select_related("procedencia"), pk=pk)
    
    if request.method == "POST":
        form = ProveedorForm(request.POST, instance=proveedor)
        
        if form.is_valid():
            try:
                proveedor = form.save()
                messages.success(request, "Proveedor actualizado exitosamente.")
                return redirect("proveedor_detail", pk=proveedor.pk)
            except Exception as e:
                messages.error(request, f"Error al actualizar el proveedor: {e}")
        else:
            messages.error(request, "Error en el formulario. Por favor corrige los errores.")
    else:
        form = ProveedorForm(instance=proveedor)
    
    context = {
        "form": form,
        "title": f"Editar Proveedor {proveedor.nombre}",
        "proveedor": proveedor,
        "is_edit": True
    }
    return render(request, "liquidaciones/proveedor_form.html", context)


def proveedor_delete(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == "POST":
        nombre = proveedor.nombre
        proveedor.delete()
        messages.success(request, f"Proveedor {nombre} eliminado exitosamente.")
        return redirect("proveedor_list")
    
    context = {"proveedor": proveedor, "title": "Eliminar Proveedor"}
    return render(request, "liquidaciones/proveedor_confirm_delete.html", context)


# Procedencia CRUD Views
def procedencia_list(request):
    procedencias = Procedencia.objects.all().order_by("nombre")
    
    # Search functionality
    search = request.GET.get("search", "")
    if search:
        procedencias = procedencias.filter(nombre__icontains=search)
    
    # Pagination
    paginator = Paginator(procedencias, 10)  # Show 10 procedencias per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
        "title": "Lista de Procedencias"
    }
    return render(request, "liquidaciones/procedencia_list.html", context)


def procedencia_create(request):
    if request.method == "POST":
        form = ProcedenciaForm(request.POST)
        
        if form.is_valid():
            try:
                procedencia = form.save()
                messages.success(request, f"Procedencia {procedencia.nombre} creada exitosamente.")
                return redirect("procedencia_list")
            except Exception as e:
                messages.error(request, f"Error al crear la procedencia: {e}")
        else:
            messages.error(request, "Error en el formulario. Por favor corrige los errores.")
    else:
        form = ProcedenciaForm()
    
    context = {"form": form, "title": "Crear Procedencia"}
    return render(request, "liquidaciones/procedencia_form.html", context)


def procedencia_detail(request, pk):
    procedencia = get_object_or_404(Procedencia, pk=pk)
    return render(request, "liquidaciones/procedencia_detail.html", {"procedencia": procedencia})


def procedencia_edit(request, pk):
    procedencia = get_object_or_404(Procedencia, pk=pk)
    
    if request.method == "POST":
        form = ProcedenciaForm(request.POST, instance=procedencia)
        
        if form.is_valid():
            try:
                procedencia = form.save()
                messages.success(request, "Procedencia actualizada exitosamente.")
                return redirect("procedencia_detail", pk=procedencia.pk)
            except Exception as e:
                messages.error(request, f"Error al actualizar la procedencia: {e}")
        else:
            messages.error(request, "Error en el formulario. Por favor corrige los errores.")
    else:
        form = ProcedenciaForm(instance=procedencia)
    
    context = {
        "form": form,
        "title": f"Editar Procedencia {procedencia.nombre}",
        "procedencia": procedencia,
        "is_edit": True
    }
    return render(request, "liquidaciones/procedencia_form.html", context)


def procedencia_delete(request, pk):
    procedencia = get_object_or_404(Procedencia, pk=pk)
    
    if request.method == "POST":
        nombre = procedencia.nombre
        procedencia.delete()
        messages.success(request, f"Procedencia {nombre} eliminada exitosamente.")
        return redirect("procedencia_list")
    
    context = {"procedencia": procedencia, "title": "Eliminar Procedencia"}
    return render(request, "liquidaciones/procedencia_confirm_delete.html", context)


# PlanillaGastos CRUD Views
def planilla_gastos_list(request):
    planillas = PlanillaGastos.objects.all().order_by("-fecha")
    
    # Search functionality
    search = request.GET.get("search", "")
    if search:
        planillas = planillas.filter(
            models.Q(numero_planilla__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(planillas, 10)  # Show 10 planillas per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "search": search,
        "title": "Lista de Planillas de Gastos"
    }
    return render(request, "liquidaciones/planilla_gastos_list.html", context)


def planilla_gastos_create(request):
    if request.method == "POST":
        print("=== PLANILLA GASTOS CREATE VIEW CALLED ===")
        print("Request method:", request.method)
        print("POST data keys:", list(request.POST.keys()))
        print("POST data values:", {k: v for k, v in request.POST.items() if k != "csrfmiddlewaretoken"})
        
        form = PlanillaGastosForm(request.POST)
        formset = PlanillaGastosItemFormSet(request.POST)
        
        print("Form valid:", form.is_valid())
        if not form.is_valid():
            print("Form errors:", dict(form.errors))

        print("Formset valid:", formset.is_valid())
        if not formset.is_valid():
            print("Formset errors:", [dict(f.errors) for f in formset])
            print("Formset non_form_errors:", formset.non_form_errors())
        
        if form.is_valid() and formset.is_valid():
            try:
                planilla = form.save()
                
                # Only save forms that have a description
                instances = formset.save(commit=False)
                print(f"✅ Formset instances to process: {len(instances)}")
                saved_items = []
                
                for i, instance in enumerate(instances):
                    print(f"Processing instance {i}: descripcion='{instance.descripcion}', monto='{instance.monto}'")
                    if instance.descripcion:  # Only save if description is provided
                        instance.planilla_gastos = planilla
                        # Ensure numeric fields have default values if empty
                        if not instance.monto:
                            instance.monto = 0
                        instance.save()
                        saved_items.append(instance)
                        print(f"✅ Saved instance {i}: {instance.descripcion}")
                    else:
                        print(f"⚠️ Skipping instance {i}: no description")
                
                # Also handle formset deletions
                for obj in formset.deleted_objects:
                    obj.delete()
                
                # Show appropriate message
                if saved_items:
                    messages.success(
                        request,
                        f"Planilla de Gastos {planilla.numero_planilla} creada exitosamente con {len(saved_items)} item(s).",
                    )
                else:
                    messages.success(
                        request,
                        f"Planilla de Gastos {planilla.numero_planilla} creada exitosamente.",
                    )
                    messages.info(
                        request,
                        "No se agregaron items a esta planilla. Puedes editarla para agregar items más tarde.",
                    )
                
                return redirect("planilla_gastos_list")
                
            except Exception as e:
                print(f"❌ ERROR DURING PLANILLA GASTOS SAVE: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, f"Error al guardar la planilla: {e}")
        else:
            if not form.is_valid():
                messages.error(request, f"Error en el formulario principal: {form.errors}")
            if not formset.is_valid():
                messages.error(request, f"Error en los items: {formset.errors}")
    else:
        form = PlanillaGastosForm()
        # For create, we want one empty form to start with
        formset = PlanillaGastosItemFormSet(queryset=PlanillaGastosItem.objects.none())
        formset.extra = 1
    
    context = {"form": form, "formset": formset, "title": "Crear Planilla de Gastos"}
    return render(request, "liquidaciones/planilla_gastos_form.html", context)


def planilla_gastos_detail(request, pk):
    planilla = get_object_or_404(PlanillaGastos, pk=pk)
    return render(request, "liquidaciones/planilla_gastos_detail.html", {"planilla": planilla})


def planilla_gastos_edit(request, pk):
    planilla = get_object_or_404(PlanillaGastos, pk=pk)
    
    if request.method == "POST":
        print(f"=== PLANILLA GASTOS EDIT VIEW CALLED (PK: {pk}) ===")
        print("Request method:", request.method)
        print("POST data keys:", list(request.POST.keys()))
        print("POST data values:", {k: v for k, v in request.POST.items() if k != "csrfmiddlewaretoken"})
        
        form = PlanillaGastosForm(request.POST, instance=planilla)
        formset = PlanillaGastosItemFormSet(request.POST, instance=planilla)
        
        print("Form valid:", form.is_valid())
        if not form.is_valid():
            print("Form errors:", dict(form.errors))

        # Check formset forms before validation
        print(f"Number of forms in formset: {len(formset.forms)}")
        for i, form_instance in enumerate(formset.forms):
            print(f"Form {i} initial data: {form_instance.initial}")
            if hasattr(form_instance, 'instance') and form_instance.instance.pk:
                print(f"Form {i} instance: {form_instance.instance.pk} - {form_instance.instance}")

        print("Formset valid:", formset.is_valid())
        if not formset.is_valid():
            print("Formset errors:", [dict(f.errors) for f in formset])
            print("Formset non_form_errors:", formset.non_form_errors())
            # Check individual form validity
            for i, form_instance in enumerate(formset.forms):
                print(f"Form {i} valid: {form_instance.is_valid()}")
                if not form_instance.is_valid():
                    print(f"Form {i} errors: {dict(form_instance.errors)}")
                print(f"Form {i} cleaned_data: {getattr(form_instance, 'cleaned_data', 'No cleaned_data')}")
        
        if form.is_valid() and formset.is_valid():
            try:
                planilla = form.save()
                
                # Only save non-empty forms
                instances = formset.save(commit=False)
                print(f"✅ Formset instances to process: {len(instances)}")
                
                # Also check what forms were processed
                print("Formset forms that will be processed:")
                for i, form_instance in enumerate(formset.forms):
                    if hasattr(form_instance, 'cleaned_data'):
                        descripcion = form_instance.cleaned_data.get('descripcion', '')
                        monto = form_instance.cleaned_data.get('monto', '')
                        delete_checked = form_instance.cleaned_data.get('DELETE', False)
                        print(f"Form {i}: descripcion='{descripcion}', monto='{monto}', DELETE={delete_checked}")
                
                saved_items = []
                for i, instance in enumerate(instances):
                    print(f"Processing instance {i}: descripcion='{instance.descripcion}', monto='{instance.monto}', pk='{instance.pk}'")
                    if instance.descripcion:  # Only save if description is provided
                        # Ensure numeric fields have default values if empty
                        if not instance.monto:
                            instance.monto = 0
                        instance.save()
                        saved_items.append(instance)
                        print(f"✅ Saved instance {i}: {instance.descripcion}")
                    else:
                        print(f"⚠️ Skipping instance {i}: no description")
                
                # Delete items marked for deletion
                print(f"Items marked for deletion: {len(formset.deleted_objects)}")
                for i, obj in enumerate(formset.deleted_objects):
                    print(f"Deleting item {i}: {obj.descripcion} - {obj.monto}")
                    obj.delete()
                
                messages.success(request, "Planilla de Gastos actualizada exitosamente.")
                return redirect("planilla_gastos_detail", pk=planilla.pk)
                
            except Exception as e:
                print(f"❌ ERROR DURING PLANILLA GASTOS UPDATE: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, f"Error al actualizar la planilla: {e}")
        else:
            if not form.is_valid():
                messages.error(request, f"Error en el formulario principal: {form.errors}")
            if not formset.is_valid():
                messages.error(request, f"Error en los items: {formset.errors}")
    else:
        form = PlanillaGastosForm(instance=planilla)
        # For edit, only show existing items, no extra forms
        formset = PlanillaGastosItemFormSet(instance=planilla)
        formset.extra = 0
    
    context = {
        "form": form,
        "formset": formset,
        "title": f"Editar Planilla de Gastos {planilla.numero_planilla}",
        "planilla": planilla,
        "is_edit": True,
    }
    return render(request, "liquidaciones/planilla_gastos_form.html", context)


def planilla_gastos_delete(request, pk):
    planilla = get_object_or_404(PlanillaGastos, pk=pk)
    
    if request.method == "POST":
        numero_planilla = planilla.numero_planilla
        planilla.delete()
        messages.success(request, f"Planilla de Gastos {numero_planilla} eliminada exitosamente.")
        return redirect("planilla_gastos_list")
    
    context = {"planilla": planilla, "title": "Eliminar Planilla de Gastos"}
    return render(request, "liquidaciones/planilla_gastos_confirm_delete.html", context)


def planilla_gastos_autocomplete(request):
    query = request.GET.get("q", "")
    planilla_id = request.GET.get("id", "")
    
    if planilla_id:
        # Fetch specific planilla by ID for restoration after form errors
        try:
            planilla = PlanillaGastos.objects.get(id=planilla_id)
            results = [
                {
                    "id": planilla.id,
                    "text": f"{planilla.numero_planilla} - {planilla.fecha} (Total: {planilla.total_gastos:,.0f})",
                }
            ]
        except PlanillaGastos.DoesNotExist:
            results = []
    elif query:
        planillas = PlanillaGastos.objects.filter(
            numero_planilla__icontains=query
        )[:10]
        results = [
            {
                "id": planilla.id,
                "text": f"{planilla.numero_planilla} - {planilla.fecha} (Total: {planilla.total_gastos:,.0f})",
            }
            for planilla in planillas
        ]
    else:
        results = []
    
    return JsonResponse({"results": results})

