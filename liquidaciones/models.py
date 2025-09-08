from django.db import models

from clientes.models import Cliente
from items.models import Item


class Procedencia(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    procedencia = models.ForeignKey(
        Procedencia,
        on_delete=models.PROTECT,
        default=None,
        null=True,
    )

    def __str__(self):
        return self.nombre


class Liquidacion(models.Model):
    class ClaseChoices(models.TextChoices):
        IMPORTACION = "importacion", "Importación"
        EXPORTACION = "exportacion", "Exportación"

    class MonedaChoices(models.TextChoices):
        USD = "USD", "USD"
        EURO = "EURO", "EURO"
        GUARANIES = "GUARANIES", "Guaraníes"

    fecha = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero_liquidacion = models.CharField(max_length=50)
    numero_despacho = models.CharField(max_length=50)
    clase = models.CharField(max_length=20, choices=ClaseChoices.choices)
    numero_factura_comercial = models.CharField(max_length=50)
    partida_arancelaria = models.CharField(max_length=50)
    ad_valorem = models.CharField(max_length=50)
    valor_imponible = models.DecimalField(max_digits=12, decimal_places=2)
    moneda_valor_imponible = models.CharField(
        max_length=10, choices=MonedaChoices.choices
    )
    equivalente_gs = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_cambio = models.CharField(max_length=20)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    @property
    def procedencia(self):
        """Accede a la procedencia a través del proveedor"""
        return self.proveedor.procedencia

    @property
    def total_monto(self):
        """Suma de todos los montos de los items"""
        return sum(item.monto for item in self.liquidacionitem_set.all())

    @property
    def total_iva(self):
        """Suma de todos los IVA de los items"""
        return sum(item.iva for item in self.liquidacionitem_set.all())

    @property
    def total_retencion(self):
        """Suma de todas las retenciones de los items"""
        return sum(item.retencion for item in self.liquidacionitem_set.all())

    @property
    def valor_total_calculado(self):
        """
        Calcula el valor total como la suma de subtotales de todos los items de la liquidación
        """
        return sum(item.subtotal for item in self.liquidacionitem_set.all())

    def __str__(self):
        return f"Liquidación {self.numero_liquidacion} - {self.cliente.nombre}"


class LiquidacionItem(models.Model):
    liquidacion = models.ForeignKey(Liquidacion, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    retencion = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return self.monto + self.iva + self.retencion

    def __str__(self):
        return f"{self.item.descripcion} - {self.subtotal}"


class Banco(models.Model):
    nombre = models.CharField(max_length=255)
    titular = models.CharField(max_length=255)
    numero_cuenta = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} - {self.titular}"


class Pago(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="pagos")
    banco = models.ForeignKey(Banco, on_delete=models.CASCADE)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    referencia = models.CharField(max_length=100, blank=True)
    concepto = models.TextField(blank=True)

    class Meta:
        ordering = ["fecha"]

    def __str__(self):
        return f"Pago {self.cliente.nombre} - {self.monto} ({self.fecha})"
