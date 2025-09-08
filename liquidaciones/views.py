from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import models
from .models import Liquidacion, LiquidacionItem, Proveedor
from .forms import LiquidacionForm, LiquidacionItemFormSet
from items.models import Item
from clientes.models import Cliente


def liquidacion_create(request):
    print("=== LIQUIDACION CREATE VIEW CALLED ===")
    print("Request method:", request.method)
    
    if request.method == 'POST':
        print("=== POST REQUEST RECEIVED ===")
        print("POST data keys:", list(request.POST.keys()))
        print("POST data values:", {k: v for k, v in request.POST.items() if k != 'csrfmiddlewaretoken'})
        
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
                    messages.success(request, f'Liquidación {liquidacion.numero_liquidacion} creada exitosamente con {len(saved_items)} item(s).')
                else:
                    messages.success(request, f'Liquidación {liquidacion.numero_liquidacion} creada exitosamente.')
                    messages.info(request, 'No se agregaron items a esta liquidación. Puedes editarla para agregar items más tarde.')
                
                print("=== REDIRECTING TO LIQUIDACION_LIST ===")
                redirect_response = redirect('liquidacion_list')
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
                messages.error(request, f'Error en el formulario principal: {form.errors}')
            if not formset.is_valid():
                messages.error(request, f'Error en los items: {formset.errors}')
    else:
        print("=== GET REQUEST - RENDERING EMPTY FORM ===")
        form = LiquidacionForm()
        # For create, we want one empty form to start with
        formset = LiquidacionItemFormSet(queryset=LiquidacionItem.objects.none())
        formset.extra = 1
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Crear Liquidación'
    }
    return render(request, 'liquidaciones/liquidacion_form.html', context)


def liquidacion_detail(request, pk):
    liquidacion = get_object_or_404(Liquidacion, pk=pk)
    return render(request, 'liquidaciones/liquidacion_detail.html', {'liquidacion': liquidacion})


def liquidacion_edit(request, pk):
    print(f"=== LIQUIDACION EDIT VIEW CALLED (PK: {pk}) ===")
    print("Request method:", request.method)
    
    liquidacion = get_object_or_404(Liquidacion, pk=pk)
    
    if request.method == 'POST':
        print("=== POST REQUEST RECEIVED FOR EDIT ===")
        print("POST data keys:", list(request.POST.keys()))
        print("POST data values:", {k: v for k, v in request.POST.items() if k != 'csrfmiddlewaretoken'})
        
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
                for obj in formset.deleted_objects:
                    obj.delete()
                    print(f"✅ Deleted item: {obj}")
                    
                messages.success(request, 'Liquidación actualizada exitosamente.')
                print("=== REDIRECTING TO LIQUIDACION_DETAIL ===")
                redirect_response = redirect('liquidacion_detail', pk=liquidacion.pk)
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
                messages.error(request, f'Error en el formulario principal: {form.errors}')
            if not formset.is_valid():
                messages.error(request, f'Error en los items: {formset.errors}')
    else:
        form = LiquidacionForm(instance=liquidacion)
        # For edit, only show existing items, no extra forms
        formset = LiquidacionItemFormSet(instance=liquidacion)
        formset.extra = 0
    
    context = {
        'form': form,
        'formset': formset,
        'title': f'Editar Liquidación {liquidacion.numero_liquidacion}',
        'liquidacion': liquidacion,
        'is_edit': True
    }
    return render(request, 'liquidaciones/liquidacion_form.html', context)


def liquidacion_delete(request, pk):
    liquidacion = get_object_or_404(Liquidacion, pk=pk)
    
    if request.method == 'POST':
        numero_liquidacion = liquidacion.numero_liquidacion
        liquidacion.delete()
        messages.success(request, f'Liquidación {numero_liquidacion} eliminada exitosamente.')
        return redirect('liquidacion_list')
    
    context = {
        'liquidacion': liquidacion,
        'title': 'Eliminar Liquidación'
    }
    return render(request, 'liquidaciones/liquidacion_confirm_delete.html', context)


def liquidacion_list(request):
    liquidaciones = Liquidacion.objects.all().order_by('-fecha')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        liquidaciones = liquidaciones.filter(
            models.Q(numero_liquidacion__icontains=search) |
            models.Q(cliente__nombre__icontains=search) |
            models.Q(numero_despacho__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(liquidaciones, 10)  # Show 10 liquidaciones per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'title': 'Lista de Liquidaciones'
    }
    return render(request, 'liquidaciones/liquidacion_list.html', context)


def item_autocomplete(request):
    query = request.GET.get('q', '')
    item_id = request.GET.get('id', '')
    
    if item_id:
        # Fetch specific item by ID for restoration after form errors
        try:
            item = Item.objects.get(id=item_id)
            results = [{'id': item.id, 'text': item.descripcion}]
        except Item.DoesNotExist:
            results = []
    elif query:
        items = Item.objects.filter(descripcion__icontains=query)[:10]
        results = [{'id': item.id, 'text': item.descripcion} for item in items]
    else:
        results = []
    
    return JsonResponse({'results': results})


def cliente_autocomplete(request):
    query = request.GET.get('q', '')
    if query:
        clientes = Cliente.objects.filter(nombre__icontains=query)[:10]
        results = [{'id': cliente.id, 'text': cliente.nombre} for cliente in clientes]
    else:
        results = []
    
    return JsonResponse({'results': results})


def proveedor_autocomplete(request):
    query = request.GET.get('q', '')
    if query:
        proveedores = Proveedor.objects.select_related('procedencia').filter(
            models.Q(nombre__icontains=query) |
            models.Q(procedencia__nombre__icontains=query)
        )[:10]
        
        results = []
        for proveedor in proveedores:
            procedencia_nombre = proveedor.procedencia.nombre if proveedor.procedencia else "Sin especificar"
            results.append({
                'id': proveedor.id, 
                'text': f"{proveedor.nombre} ({procedencia_nombre})"
            })
    else:
        results = []
    
    return JsonResponse({'results': results})


