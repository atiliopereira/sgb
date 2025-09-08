from django.contrib import admin
from .models import Procedencia, Proveedor, Liquidacion, LiquidacionItem, Banco, Pago


@admin.register(Procedencia)
class ProcedenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'procedencia')
    search_fields = ('nombre', 'procedencia__nombre')
    list_filter = ('procedencia',)


class LiquidacionItemInline(admin.TabularInline):
    model = LiquidacionItem
    fields = ('item', 'monto', 'iva', 'retencion')
    extra = 1
    readonly_fields = ('subtotal_display',)
    
    def subtotal_display(self, obj):
        return obj.subtotal if obj else 0
    subtotal_display.short_description = 'Subtotal'


@admin.register(Liquidacion)
class LiquidacionAdmin(admin.ModelAdmin):
    list_display = ('numero_liquidacion', 'fecha', 'cliente', 'clase', 'valor_imponible')
    list_filter = ('fecha', 'clase', 'moneda_valor_imponible')
    search_fields = ('numero_liquidacion', 'cliente__nombre', 'numero_despacho')
    inlines = [LiquidacionItemInline]
    date_hierarchy = 'fecha'


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'titular', 'numero_cuenta')
    search_fields = ('nombre', 'titular', 'numero_cuenta')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'fecha', 'monto', 'banco', 'referencia')
    list_filter = ('fecha', 'banco')
    search_fields = ('cliente__nombre', 'referencia', 'concepto')
    date_hierarchy = 'fecha'
