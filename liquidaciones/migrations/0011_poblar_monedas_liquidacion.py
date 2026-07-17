from django.db import migrations

MONEDAS = ["USD", "EURO", "PYG", "BRL"]


def poblar_monedas_liquidacion(apps, schema_editor):
    Moneda = apps.get_model("liquidaciones", "Moneda")
    Liquidacion = apps.get_model("liquidaciones", "Liquidacion")
    guaranies = Moneda.objects.get(codigo="PYG")
    for codigo in MONEDAS:
        moneda = Moneda.objects.get(codigo=codigo)
        Liquidacion.objects.filter(moneda_valor_imponible_old=codigo).update(
            moneda_valor_imponible=moneda
        )
    # Cualquier valor no reconocido cae en Guaraníes para no dejar filas nulas
    Liquidacion.objects.filter(moneda_valor_imponible__isnull=True).update(
        moneda_valor_imponible=guaranies
    )
    Liquidacion.objects.update(moneda_factura=guaranies)


def revertir_monedas_liquidacion(apps, schema_editor):
    Liquidacion = apps.get_model("liquidaciones", "Liquidacion")
    for liquidacion in Liquidacion.objects.select_related("moneda_valor_imponible"):
        liquidacion.moneda_valor_imponible_old = (
            liquidacion.moneda_valor_imponible.codigo
        )
        liquidacion.save(update_fields=["moneda_valor_imponible_old"])


class Migration(migrations.Migration):
    """Solo datos: los UPDATE sobre liquidaciones deben correr en una
    migración sin DDL, porque las FK diferidas de Postgres dejan trigger
    events pendientes que bloquean cualquier ALTER TABLE / CREATE INDEX
    posterior en la misma transacción."""

    dependencies = [
        ("liquidaciones", "0010_moneda_model"),
    ]

    operations = [
        migrations.RunPython(poblar_monedas_liquidacion, revertir_monedas_liquidacion),
    ]
