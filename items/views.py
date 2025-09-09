from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ItemForm
from .models import Item


def item_list(request):
    items = Item.objects.all().order_by('descripcion')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        items = items.filter(descripcion__icontains=search)
    
    # Pagination
    paginator = Paginator(items, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'title': 'Lista de Items'
    }
    return render(request, 'items/item_list.html', context)


def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        
        if form.is_valid():
            try:
                item = form.save()
                messages.success(request, f'Item {item.descripcion} creado exitosamente.')
                return redirect('item_list')
            except Exception as e:
                messages.error(request, f'Error al crear el item: {e}')
        else:
            messages.error(request, 'Error en el formulario. Por favor corrige los errores.')
    else:
        form = ItemForm()
    
    context = {'form': form, 'title': 'Crear Item'}
    return render(request, 'items/item_form.html', context)


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'items/item_detail.html', {'item': item})


def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        
        if form.is_valid():
            try:
                item = form.save()
                messages.success(request, 'Item actualizado exitosamente.')
                return redirect('item_detail', pk=item.pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar el item: {e}')
        else:
            messages.error(request, 'Error en el formulario. Por favor corrige los errores.')
    else:
        form = ItemForm(instance=item)
    
    context = {
        'form': form,
        'title': f'Editar Item {item.descripcion}',
        'item': item,
        'is_edit': True
    }
    return render(request, 'items/item_form.html', context)


def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        descripcion = item.descripcion
        item.delete()
        messages.success(request, f'Item {descripcion} eliminado exitosamente.')
        return redirect('item_list')
    
    context = {'item': item, 'title': 'Eliminar Item'}
    return render(request, 'items/item_confirm_delete.html', context)
