from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'email', 'estado_cuenta_link')
    search_fields = ('nombre', 'ruc', 'email')
    
    def estado_cuenta_link(self, obj):
        url = reverse('clientes:estado_cuenta', args=[obj.pk])
        return format_html('<a href="{}" target="_blank" class="btn btn-sm btn-primary">Ver Estado de Cuenta</a>', url)
    
    estado_cuenta_link.short_description = 'Estado de Cuenta'
    estado_cuenta_link.allow_tags = True
